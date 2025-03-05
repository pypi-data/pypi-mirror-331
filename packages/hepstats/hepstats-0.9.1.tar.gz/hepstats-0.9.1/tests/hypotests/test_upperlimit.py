import pytest
import numpy as np
import os
zfit = pytest.importorskip("zfit")
from zfit.minimize import Minuit

import hepstats
from hepstats.hypotests.calculators.basecalculator import BaseCalculator
from hepstats.hypotests.calculators import AsymptoticCalculator, FrequentistCalculator
from hepstats.hypotests import UpperLimit
from hepstats.hypotests.parameters import POI, POIarray
from hepstats.hypotests.exceptions import POIRangeError

notebooks_dir = os.path.dirname(hepstats.__file__) + "/../../notebooks/hypotests"


# def create_loss():
#
#     bounds = (0.1, 3.0)
#     obs = zfit.Space("x", limits=bounds)
#
#     # Data and signal
#     np.random.seed(0)
#     tau = -2.0
#     beta = -1 / tau
#     bkg = np.random.exponential(beta, 300)
#     peak = np.random.normal(1.2, 0.1, 10)
#     data = np.concatenate((bkg, peak))
#     data = data[(data > bounds[0]) & (data < bounds[1])]
#     N = len(data)
#     data = zfit.data.Data.from_numpy(obs=obs, array=data)
#
#     lambda_ = zfit.Parameter("lambda", -2.0, -10.0, -0.1)
#     Nsig = zfit.Parameter("Nsig", 20.0, -20.0, N)
#     Nbkg = zfit.Parameter("Nbkg", N, 0.0, N * 2)
#
#     signal = zfit.pdf.Gauss(obs=obs, mu=1.2, sigma=0.1).create_extended(Nsig)
#     background = zfit.pdf.Exponential(obs=obs, lambda_=lambda_).create_extended(Nbkg)
#     tot_model = zfit.pdf.SumPDF([signal, background])
#
#     loss = ExtendedUnbinnedNLL(model=tot_model, data=data)
#
#     return loss, (Nsig, Nbkg)


def test_constructor(create_loss):
    with pytest.raises(TypeError):
        UpperLimit()

    loss, (Nsig, Nbkg, _, _) = create_loss(npeak=10)
    calculator = BaseCalculator(loss, Minuit())

    poi_1 = POI(Nsig, 0.0)
    poi_2 = POI(Nsig, 2.0)

    with pytest.raises(TypeError):
        UpperLimit(calculator)

    with pytest.raises(TypeError):
        UpperLimit(calculator, poi_1)

    with pytest.raises(TypeError):
        UpperLimit(calculator, [poi_1], poi_2)


class AsymptoticCalculatorOld(AsymptoticCalculator):
    UNBINNED_TO_BINNED_LOSS = {}


def asy_calc(create_loss, nbins):
    loss, (Nsig, Nbkg, mean, sigma) = create_loss(npeak=10, nbins=nbins)
    mean.floating = False
    sigma.floating = False
    return Nsig, AsymptoticCalculator(loss, Minuit())


def asy_calc_old(create_loss, nbins):
    loss, (Nsig, Nbkg, mean, sigma) = create_loss(npeak=10, nbins=nbins)
    mean.floating = False
    sigma.floating = False
    return Nsig, AsymptoticCalculatorOld(loss, Minuit())


def freq_calc(create_loss, nbins):
    loss, (Nsig, Nbkg, mean, sigma) = create_loss(npeak=10, nbins=nbins)
    mean.floating = False
    sigma.floating = False
    calculator = FrequentistCalculator.from_yaml(
        f"{notebooks_dir}/toys/upperlimit_freq_zfit_toys.yml", loss, Minuit()
    )
    # calculator = FrequentistCalculator(loss, Minuit(), ntoysnull=10000, ntoysalt=10000)
    return Nsig, calculator


@pytest.mark.parametrize(
    "nbins", [None, 73, 211], ids=lambda x: "unbinned" if x is None else f"nbins={x}"
)
@pytest.mark.parametrize("calculator", [asy_calc, freq_calc, asy_calc_old])
def test_with_gauss_exp_example(create_loss, calculator, nbins):
    if calculator is asy_calc_old and nbins is not None:
        pytest.skip("Old asymptotic calculator does not support binned loss")
    Nsig, calculator = calculator(create_loss, nbins)

    poinull = POIarray(Nsig, np.linspace(0.0, 25, 15))
    poialt = POI(Nsig, 0)

    ul = UpperLimit(calculator, poinull, poialt)
    ul_qtilde = UpperLimit(calculator, poinull, poialt, qtilde=True)
    limits = ul.upperlimit(alpha=0.05, CLs=True)

    assert limits["observed"] == pytest.approx(16.7, rel=0.15)
    assert limits["expected"] == pytest.approx(11.5, rel=0.15)
    assert limits["expected_p1"] == pytest.approx(16.729552184042365, rel=0.1)
    assert limits["expected_p2"] == pytest.approx(23.718823517614066, rel=0.15)
    assert limits["expected_m1"] == pytest.approx(7.977175378979202, rel=0.1)
    assert limits["expected_m2"] == pytest.approx(5.805298972983304, rel=0.15)

    ul.upperlimit(alpha=0.05, CLs=False)
    ul_qtilde.upperlimit(alpha=0.05, CLs=True)

    # test error when scan range is too small

    with pytest.raises(POIRangeError):
        poinull = POIarray(Nsig, poinull.values[:5])
        ul = UpperLimit(calculator, poinull, poialt)
        ul.upperlimit(alpha=0.05, CLs=True)
