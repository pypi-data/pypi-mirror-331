from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np

import dcmri.ui as ui
import dcmri.lib as lib
import dcmri.sig as sig
import dcmri.utils as utils
import dcmri.pk as pk
import dcmri.pk_aorta as pk_aorta
import dcmri.kidney as kidney


class AortaKidneys(ui.Model):
    """Joint model for aorta and kidneys signals.

    The model represents the kidneys as a two-compartment filtration system and the body as a leaky loop with a heart-lung system and an organ system. The heart-lung system is modelled as a chain compartment and the organs are modelled as a compartment or a two-compartment exchange model. Bolus injection into the system is modelled as a step function.

        **Injection parameters**

        - **weight** (float, default=70): Subject weight in kg.
        - **agent** (str, default='gadoterate'): Contrast agent generic name.
        - **dose** (float, default=0.2): Injected contrast agent dose in mL per kg bodyweight.
        - **rate** (float, default=1): Contrast agent injection rate in mL per sec.

        **Acquisition parameters**

        - **sequence** (str, default='SS'): Signal model.
        - **tmax** (float, default=120): Maximum acquisition time in sec.
        - **tacq** (float, default=None): Time to acquire a single dynamic in the first scan (sec). If this is not provided, tacq is taken from the difference between the first two data points.
        - **field_strength** (float, default=3.0): Magnetic field strength in T. 
        - **n0** (float, default=1): Baseline length in nr of scans.
        - **TR** (float, default=0.005): Repetition time, or time between excitation pulses, in sec. 
        - **FA** (float, default=15): Nominal flip angle in degrees.
        - **TC** (float, default=0.1): Time to the center of k-space in a saturation-recovery sequence.

        **Signal parameters**

        - **R10a** (float, default=1): Precontrast arterial relaxation rate in 1/sec. 
        - **S0b** (float, default=1): scale factor for the arterial MR signal in the first scan. 
        - **R10_lk** (float, default=1): Baseline R1 for the left kidney.
        - **S0_lk** (float, default=1): Scale factor for the left kidney signal. 
        - **R10_rk** (float, default=1): Baseline R1 for the right kidney.
        - **S0_rk** (float, default=1): Scale factor for the right kidney signal.   

        **Whole body kinetic parameters**

        - **organs** (str, default='2cxm'): Kinetic model for the organs.
        - **BAT** (float, default=60): Bolus arrival time, i.e. time point where the indicator first arrives in the body. 
        - **BAT2** (float, default=1200): Bolus arrival time in the second scan, i.e. time point where the indicator first arrives in the body. 
        - **CO** (float, default=100): Cardiac output in mL/sec.
        - **Eb** (float, default=0.05): fraction of indicator extracted from the vasculature in a single pass. 
        - **Thl** (float, default=10): Mean transit time through heart and lungs.
        - **Dhl** (float, default=0.2): Dispersion through the heart-lung system, with a value in the range [0,1].
        - **To** (float, default=20): average time to travel through the organ's vasculature.
        - **Eo** (float, default=0.15): Fraction of indicator entering the organs which is extracted from the blood pool.
        - **Teb** (float, default=120): Average time to travel through the organs extravascular space.

        **Kidney kinetic parameters**

        - **kinetics** (str, default='2CFM'). Kidney kinetic model (only one option at this stage).
        - **Hct** (float, default=0.45): Hematocrit.
        - **Fp_lk** (Plasma flow, mL/sec/cm3): Flow of plasma into the plasma compartment (left kidney).
        - **Tp_lk** (Plasma mean transit time, sec): Transit time of the plasma compartment (left kidney). 
        - **Ft_lk** (Tubular flow, mL/sec/cm3): Flow of fluid into the tubuli (left kidney).
        - **Tt_lk** (Tubular mean transit time, sec): Transit time of the tubular compartment (left kidney).
        - **Ta_lk** (Arterial delay time, sec): Transit time through the arterial compartment (left kidney). 
        - **Fp_rk** (Plasma flow, mL/sec/cm3): Flow of plasma into the plasma compartment (right kidney).
        - **Tp_rk** (Plasma mean transit time, sec): Transit time of the plasma compartment (right kidney). 
        - **Ft_rk** (Tubular flow, mL/sec/cm3): Flow of fluid into the tubuli (right kidney).
        - **Tt_rk** (Tubular mean transit time, sec): Transit time of the tubular compartment (right kidney).
        - **Ta_rk** (Arterial delay time, sec): Transit time through the arterial compartment (right kidney). 

        **Prediction and training parameters**

        - **dt** (float, default=1): Internal time resolution of the AIF in sec. 
        - **dose_tolerance** (fload, default=0.1): Stopping criterion for the whole-body model.
        - **free** (array-like): list of free parameters. The default depends on the kinetics parameter.
        - **free** (array-like): 2-element list with lower and upper free of the free parameters. The default depends on the kinetics parameter.

        **Additional parameters**

        - **vol_lk** (float, optional): Kidney volume in cm3 (left kidney).
        - **vol_rk** (float, optional): Kidney volume in cm3 (right kidney).

    Args:
        params (dict, optional): override defaults for any of the parameters.

    See Also:
        `AortaLiver`

    Example:

        Use the model to reconstruct concentrations from experimentally derived signals.

    .. plot::
        :include-source:
        :context: close-figs

        >>> import matplotlib.pyplot as plt
        >>> import dcmri as dc

        Use `fake_tissue` to generate synthetic test data from experimentally-derived concentrations:

        >>> time, aif, roi, gt = dc.fake_tissue()
        >>> xdata, ydata = (time,time,time), (aif,roi,roi)

        Build an aorta-kidney model and parameters to match the conditions of the fake tissue data:

        >>> model = dc.AortaKidneys(
        ...     dt = 0.5,
        ...     tmax = 180,
        ...     weight = 70,
        ...     agent = 'gadodiamide',
        ...     dose = 0.2,
        ...     rate = 3,
        ...     field_strength = 3.0,
        ...     t0 = 10,
        ...     TR = 0.005,
        ...     FA = 15,
        ... )

        Train the model on the data:

        >>> model.train(xdata, ydata, xtol=1e-3)

        Plot the reconstructed signals and concentrations and compare against the experimentally derived data:

        >>> model.plot(xdata, ydata)

    """

    def __init__(self, organs='comp', heartlung='pfcomp', 
                 kidneys='2CF', sequence='SS', **params):

        # Configuration
        self.sequence = sequence
        self.organs = organs
        self.heartlung = heartlung
        self.kidneys = kidneys

        # Constants
        self.dt = 0.5
        self.tmax = 120
        self.dose_tolerance = 0.1
        self.weight = 70.0
        self.agent = 'gadoterate'
        self.dose = 0.025
        self.rate = 1
        self.field_strength = 3.0
        self.n0 = 1
        self.TR = 0.005
        self.FA = 15.0
        self.TC = 0.180
        self.TS = None

        # Aorta parameters
        self.R10a = 1/lib.T1(3.0, 'blood')
        self.S0b = 1
        self.BAT = 60
        self.CO = 100
        self.FF = 0.1
        self.Thl = 20
        self.Dhl = 0.2
        self.To = 20
        self.Eo = 0.15
        self.Teb = 120
        self.Hct = 0.45

        # Kidneys
        self.RPF = 10  # mL/sec
        self.DRF = 0.5
        self.DRPF = 0.5

        # Left kidney parameters
        self.R10_lk = 1/lib.T1(3.0, 'kidney')
        self.S0_lk = 1
        self.Ta_lk = 0
        self.vp_lk = 0.1
        self.Tt_lk = 300
        self.vol_lk = 150

        # Right kidney parameters
        self.R10_rk = 1/lib.T1(3.0, 'kidney')
        self.S0_rk = 1
        self.Ta_rk = 0
        self.vp_rk = 0.1
        self.Tt_rk = 300
        self.vol_rk = 150

        self.free = {
            'BAT': [0, np.inf],
            'CO': [0, 300],
            'Thl': [0, 30],
            'Dhl': [0.05, 0.95],
            'To': [0, 60],
            'FF': [0, 0.3],
            'RPF': [0, 50],
            'DRPF': [0, 1],
            'DRF': [0, 1],
            'vp_lk': [0, 0.3],
            'Tt_lk': [0, np.inf],  # 'Ta_lk',
            'vp_rk': [0, 0.3],
            'Tt_rk': [0, np.inf],  # 'Ta_rk']
        }

        # overide defaults
        for k, v in params.items():
            setattr(self, k, v)

        # Internal flag
        self._predict = None

    def _conc_aorta(self) -> np.ndarray:
        if self.organs == 'comp':
            organs = ['comp', (self.To,)]
        else:
            organs = ['2cxm', ([self.To, self.Teb], self.Eo)]
        if self.heartlung == 'comp':
            heartlung = ['comp', (self.Thl,)]
        elif self.heartlung == 'pfcomp':
            heartlung = ['pfcomp', (self.Thl, self.Dhl)]
        elif self.heartlung == 'chain':
            heartlung = ['chain', (self.Thl, self.Dhl)]
        self.t = np.arange(0, self.tmax, self.dt)
        conc = lib.ca_conc(self.agent)
        Ji = lib.ca_injection(self.t, self.weight,
                            conc, self.dose, self.rate, self.BAT)
        Jb = pk_aorta.flux_aorta(Ji, E=self.FF/(1+self.FF),
                           heartlung=heartlung, organs=organs,
                           dt=self.dt, tol=self.dose_tolerance)
        cb = Jb/self.CO
        self.ca = cb/(1-self.Hct)
        return self.t, cb

    def _relax_aorta(self):
        return _relax_aorta(self)

    def _predict_aorta(self, xdata: np.ndarray) -> np.ndarray:
        self.tmax = max(xdata)+self.dt
        if self.TS is not None:
            self.tmax += self.TS
        t, R1b = self._relax_aorta()
        if self.sequence == 'SR':
            # signal = sig.signal_free(self.S0b, R1b, self.TC, R10=self.R10a)
            signal = sig.signal_free(self.S0b, R1b, self.TC, self.FA)
        else:
            # signal = sig.signal_ss(self.S0b, R1b, self.TR, self.FA, R10=self.R10a)
            signal = sig.signal_ss(self.S0b, R1b, self.TR, self.FA)
        return utils.sample(xdata, t, signal, self.TS)

    def _conc_kidneys(self, sum=True):
        t = self.t
        ca_lk = pk.flux(self.ca, self.Ta_lk, t=self.t,
                        dt=self.dt, model='plug')
        ca_rk = pk.flux(self.ca, self.Ta_rk, t=self.t,
                        dt=self.dt, model='plug')
        GFR = self.RPF * self.FF
        GFR_lk = self.DRF*GFR
        GFR_rk = (1-self.DRF)*GFR
        if self.kidneys == '2CF':
            RPF_lk = self.DRPF*self.RPF
            RPF_rk = (1-self.DRPF)*self.RPF
            Tp_lk = self.vp_lk*self.vol_lk/RPF_lk
            Tp_rk = self.vp_rk*self.vol_rk/RPF_rk
            # TODO reparametrize conc_kidney 2CF with vp instead of Tp
            Nlk = kidney.conc_kidney(ca_lk, RPF_lk, Tp_lk, GFR_lk, self.Tt_lk,
                                 t=self.t, dt=self.dt, sum=sum, kinetics='2CF')
            Nrk = kidney.conc_kidney(ca_rk, RPF_rk, Tp_rk, GFR_rk, self.Tt_rk,
                                 t=self.t, dt=self.dt, sum=sum, kinetics='2CF')
        if self.kidneys == 'HF':
            Nlk = kidney.conc_kidney(ca_lk, self.vp_lk*self.vol_lk, GFR_lk,
                                 self.Tt_lk, t=self.t, dt=self.dt, sum=sum, kinetics='HF')
            Nrk = kidney.conc_kidney(ca_rk, self.vp_rk*self.vol_rk, GFR_rk,
                                 self.Tt_rk, t=self.t, dt=self.dt, sum=sum, kinetics='HF')
        return t, Nlk/self.vol_rk, Nrk/self.vol_rk

    def _relax_kidneys(self):
        t, Clk, Crk = self._conc_kidneys()
        rp = lib.relaxivity(self.field_strength, 'plasma', self.agent)
        return t, self.R10_lk + rp*Clk, self.R10_rk + rp*Crk

    def _predict_kidneys(self, xdata: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        t, R1_lk, R1_rk = self._relax_kidneys()
        if self.sequence == 'SR':
            signal_lk = sig.signal_spgr(
                self.S0_lk, R1_lk, self.TC, self.TR, self.FA)
            signal_rk = sig.signal_spgr(
                self.S0_rk, R1_rk, self.TC, self.TR, self.FA)
        else:
            signal_lk = sig.signal_ss(self.S0_lk, R1_lk, self.TR, self.FA)
            signal_rk = sig.signal_ss(self.S0_rk, R1_rk, self.TR, self.FA)
        return (
            utils.sample(xdata[0], t, signal_lk, self.TS),
            utils.sample(xdata[1], t, signal_rk, self.TS))

    def conc(self, sum=True):
        """Concentrations in aorta and kidney.

        Args:
            sum (bool, optional): If set to true, the kidney concentrations are the sum over all compartments. If set to false, the compartmental concentrations are returned individually. Defaults to True.

        Returns:
            tuple: time points, aorta blood concentrations, left kidney concentrations, right kidney concentrations.
        """
        t, cb = self._conc_aorta()
        t, Clk, Crk = self._conc_kidneys(sum=sum)
        return t, cb, Clk, Crk

    def relax(self):
        """Relaxation rates in aorta and kidney.

        Returns:
            tuple: time points, aorta relaxation rate, left kidney relaxation rate, right kidney relaxation rate.
        """
        t, R1b = self._relax_aorta()
        t, R1_lk, R1_rk = self._relax_kidneys()
        return t, R1b, R1_lk, R1_rk

    def predict(self, xdata: tuple) -> tuple:
        """Predict the data at given xdata

        Args:
            xdata (tuple): Tuple of 3 arrays with time points for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and value.

        Returns:
            tuple: Tuple of 3 arrays with signals for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and value but each has to have the same length as its corresponding array of time points.
        """
        # Public interface
        if self._predict is None:
            signala = self._predict_aorta(xdata[0])
            signal_lk, signal_rk = self._predict_kidneys((xdata[1], xdata[2]))
            return signala, signal_lk, signal_rk
        # Private interface with different input & output types
        elif self._predict == 'aorta':
            return self._predict_aorta(xdata)
        elif self._predict == 'kidneys':
            return self._predict_kidneys(xdata)

    def train(self, xdata: tuple,
              ydata: tuple, **kwargs):
        """Train the free parameters

        Args:
            xdata (tuple): Tuple of 3 arrays with time points for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and value.
            ydata (tuple): Tuple of 3 arrays with signals for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and values but each has to have the same length as its corresponding array of time points.
            kwargs: any keyword parameters accepted by `scipy.optimize.curve_fit`.

        Returns:
            Model: A reference to the model instance.
        """
        # Estimate BAT and S0b from data
        if self.sequence == 'SR':
            Srefb = sig.signal_spgr(1, self.R10a, self.TC, self.TR, self.FA)
            Sref_lk = sig.signal_spgr(1, self.R10_lk, self.TC, self.TR, self.FA)
            Sref_rk = sig.signal_spgr(1, self.R10_rk, self.TC, self.TR, self.FA)
        else:
            Srefb = sig.signal_ss(1, self.R10a, self.TR, self.FA)
            Sref_lk = sig.signal_ss(1, self.R10_lk, self.TR, self.FA)
            Sref_rk = sig.signal_ss(1, self.R10_rk, self.TR, self.FA)
        self.S0b = np.mean(ydata[0][:self.n0]) / Srefb
        self.S0_lk = np.mean(ydata[1][:self.n0]) / Sref_lk
        self.S0_rk = np.mean(ydata[2][:self.n0]) / Sref_rk
        self.BAT = xdata[0][np.argmax(ydata[0])] - (1-self.Dhl)*self.Thl
        self.BAT = max([self.BAT, 0])

        # Copy all free to restor at the end
        free = deepcopy(self.free)

        # Train free aorta parameters on aorta data
        self._predict = 'aorta'
        pars = ['BAT', 'CO', 'Thl', 'Dhl', 'To', 'Eb', 'Eo', 'Teb']
        self.free = {s: free[s] for s in pars if s in free}
        ui.train(self, xdata[0], ydata[0], **kwargs)

        # Train free kidney parameters on kidney data
        self._predict = 'kidneys'
        pars = ['RPF', 'DRPF', 'DRF',
                'vp_lk', 'Tt_lk', 'Ta_lk',
                'vp_rk', 'Tt_rk', 'Ta_rk']
        self.free = {s: free[s] for s in pars if s in free}
        ui.train(self, (xdata[1], xdata[2]), (ydata[1], ydata[2]), **kwargs)

        # Train all parameters on all data
        self._predict = None
        self.free = free
        return ui.train(self, xdata, ydata, **kwargs)

    def plot(self,
             xdata: tuple,
             ydata: tuple,
             xlim=None, ref=None,
             fname=None, show=True):
        """Plot the model fit against data

        Args:
            xdata (tuple): Tuple of 3 arrays with time points for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and value.
            ydata (tuple): Tuple of 3 arrays with signals for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and values but each has to have the same length as its corresponding array of time points.
            xlim (array_like, optional): 2-element array with lower and upper boundaries of the x-axis. Defaults to None.
            ref (tuple, optional): Tuple of optional test data in the form (x,y), where x is an array with x-values and y is an array with y-values. Defaults to None.
            fname (path, optional): Filepath to save the image. If no value is provided, the image is not saved. Defaults to None.
            show (bool, optional): If True, the plot is shown. Defaults to True.
        """
        t, cb, Clk, Crk = self.conc(sum=False)
        sig = self.predict((t, t, t))
        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)
              ) = plt.subplots(3, 2, figsize=(10, 12))
        fig.subplots_adjust(wspace=0.3)
        _plot_data1scan(t, sig[0], xdata[0], ydata[0],
                        ax1, xlim,
                        color=['lightcoral', 'darkred'],
                        test=None if ref is None else ref[0])
        _plot_data1scan(t, sig[1], xdata[1], ydata[1],
                        ax3, xlim,
                        color=['cornflowerblue', 'darkblue'],
                        test=None if ref is None else ref[1])
        _plot_data1scan(t, sig[2], xdata[2], ydata[2],
                        ax5, xlim,
                        color=['cornflowerblue', 'darkblue'],
                        test=None if ref is None else ref[2])
        _plot_conc_aorta(t, cb, ax2, xlim)
        _plot_conc_kidney(t, Clk, ax4, xlim)
        _plot_conc_kidney(t, Crk, ax6, xlim)
        if fname is not None:
            plt.savefig(fname=fname)
        if show:
            plt.show()
        else:
            plt.close()

    def export_params(self):
        pars = {}

        # Aorta
        pars['T10a'] = ['Blood precontrast T1', 1/self.R10a, "sec"]
        pars['rate'] = ['Injection rate', self.rate, "mL/sec"]
        pars['BAT'] = ['Bolus arrival time', self.BAT, "sec"]
        pars['CO'] = ['Cardiac output', self.CO, "mL/sec"]
        pars['Thl'] = ['Heart-lung mean transit time', self.Thl, "sec"]
        pars['Dhl'] = ['Heart-lung transit time dispersion', self.Dhl, ""]
        pars['To'] = ["Organs mean transit time", self.To, "sec"]
        pars['Tc'] = ["Mean circulation time", self.Thl+self.To, 'sec']
        pars['Eb'] = ["Body extraction fraction", self.FF/(1+self.FF), ""]
        pars['Eo'] = ["Organs extraction fraction", self.Eo, ""]
        pars['Teb'] = ["Organs extracellular mean transit time", self.Teb, "sec"]

        # Kidneys
        GFR = self.RPF * self.FF
        pars['GFR'] = ['Glomerular filtration rate', GFR, 'mL/sec']
        pars['RPF'] = ['Renal plasma flow', self.RPF, 'mL/sec']
        pars['DRPF'] = ['Differential renal plasma flow', self.DRPF, '']
        pars['DRF'] = ['Differential renal function', self.DRF, '']
        pars['FF'] = ['Filtration fraction', GFR/self.RPF, '']

        # Kidney LK
        RPF_lk = self.DRPF*self.RPF
        GFR_lk = self.DRF*GFR
        Tp_lk = self.vp_lk*self.vol_lk/RPF_lk
        pars['LK-RPF'] = ['LK Single-kidney plasma flow', RPF_lk, 'mL/sec']
        pars['LK-GFR'] = ['LK Single-kidney glomerular filtration rate',
                          GFR_lk, 'mL/sec']
        pars['LK-vol'] = ['LK Single-kidney volume', self.vol_lk, 'cm3']
        pars['LK-Fp'] = ['LK Plasma flow', RPF_lk/self.vol_lk, 'mL/sec/cm3']
        pars['LK-Tp'] = ['LK Plasma mean transit time', Tp_lk, 'sec']
        pars['LK-Ft'] = ['LK Tubular flow', GFR_lk/self.vol_lk, 'mL/sec/cm3']
        pars['LK-ve'] = ['LK Extracellular volume', self.vp_lk, 'mL/cm3']
        pars['LK-FF'] = ['LK Filtration fraction', GFR_lk/RPF_lk, '']
        pars['LK-E'] = ['LK Extraction fraction', GFR_lk/(GFR_lk+RPF_lk), '']
        pars['LK-Tt'] = ['LK Tubular mean transit time', self.Tt_lk, 'sec']
        pars['LK-Ta'] = ['LK Arterial mean transit time', self.Ta_lk, 'sec']

        # Kidney RK
        RPF_rk = (1-self.DRPF)*self.RPF
        GFR_rk = (1-self.DRF)*GFR
        Tp_rk = self.vp_rk*self.vol_rk/RPF_rk
        pars['RK-RPF'] = ['RK Single-kidney plasma flow', RPF_rk, 'mL/sec']
        pars['RK-GFR'] = ['RK Single-kidney glomerular filtration rate',
                          GFR_rk, 'mL/sec']
        pars['RK-vol'] = ['RK Single-kidney volume', self.vol_rk, 'cm3']
        pars['RK-Fp'] = ['RK Plasma flow', RPF_rk/self.vol_rk, 'mL/sec/cm3']
        pars['RK-Tp'] = ['RK Plasma mean transit time', Tp_rk, 'sec']
        pars['RK-Ft'] = ['RK Tubular flow', GFR_rk/self.vol_rk, 'mL/sec/cm3']
        pars['RK-ve'] = ['RK Extracellular volume', self.vp_rk, 'mL/cm3']
        pars['RK-FF'] = ['RK Filtration fraction', GFR_rk/RPF_rk, '']
        pars['RK-E'] = ['RK Extraction fraction', GFR_rk/(GFR_rk+RPF_rk), '']
        pars['RK-Tt'] = ['RK Tubular mean transit time', self.Tt_rk, 'sec']
        pars['RK-Ta'] = ['RK Arterial mean transit time', self.Ta_rk, 'sec']

        return self._add_sdev(pars)

    def cost(self, xdata: tuple, ydata: tuple, metric='NRMS') -> float:
        """Return the goodness-of-fit

        Args:
            xdata (tuple): Tuple of 3 arrays with time points for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and value.
            ydata (tuple): Tuple of 3 arrays with signals for aorta, left kidney and right kidney, in that order. The three arrays can all be different in length and values but each has to have the same length as its corresponding array of time points.
            metric (str, optional): Which metric to use - options are: 
                **RMS** (Root-mean-square);
                **NRMS** (Normalized root-mean-square); 
                **AIC** (Akaike information criterion); 
                **cAIC** (Corrected Akaike information criterion for small models);
                **BIC** (Baysian information criterion). Defaults to 'NRMS'.

        Returns:
            float: goodness of fit.
        """
        return super().cost(xdata, ydata, metric)


def _relax_aorta(self) -> np.ndarray:
    t, cb = self._conc_aorta()
    rp = lib.relaxivity(self.field_strength, 'plasma', self.agent)
    return t, self.R10a + rp*cb
    


# Helper functions for plotting

def _plot_conc_aorta(t: np.ndarray, cb: np.ndarray, ax, xlim=None):
    if xlim is None:
        xlim = [t[0], t[-1]]
    ax.set(xlabel='Time (min)', ylabel='Concentration (mM)',
           xlim=np.array(xlim)/60)
    ax.plot(t/60, 0*t, color='gray')
    ax.plot(t/60, 1000*cb, linestyle='-',
            color='darkred', linewidth=2.0, label='Aorta')
    ax.legend()


def _plot_conc_kidney(t: np.ndarray, C: np.ndarray, ax, xlim=None):
    color = 'darkblue'
    if xlim is None:
        xlim = [t[0], t[-1]]
    ax.set(xlabel='Time (min)', ylabel='Tissue concentration (mM)',
           xlim=np.array(xlim)/60)
    ax.plot(t/60, 0*t, color='gray')
    ax.plot(t/60, 1000*C[0, :], linestyle='-.',
            color=color, linewidth=2.0, label='Plasma')
    ax.plot(t/60, 1000*C[1, :], linestyle='--',
            color=color, linewidth=2.0, label='Tubuli')
    ax.plot(t/60, 1000*(C[0, :]+C[1, :]), linestyle='-',
            color=color, linewidth=2.0, label='Tissue')
    ax.legend()


def _plot_data1scan(t: np.ndarray, sig: np.ndarray,
                    xdata: np.ndarray, ydata: np.ndarray,
                    ax, xlim, color=['black', 'black'],
                    test=None):
    if xlim is None:
        xlim = [t[0], t[-1]]
    ax.set(xlabel='Time (min)', ylabel='MR Signal (a.u.)', xlim=np.array(xlim)/60)
    ax.plot(xdata/60, ydata, marker='o',
            color=color[0], label='fitted data', linestyle='None')
    ax.plot(t/60, sig, linestyle='-',
            color=color[1], linewidth=3.0, label='fit')
    if test is not None:
        ax.plot(np.array(test[0])/60, test[1], color='black',
                marker='D', linestyle='None', label='Test data')
    ax.legend()