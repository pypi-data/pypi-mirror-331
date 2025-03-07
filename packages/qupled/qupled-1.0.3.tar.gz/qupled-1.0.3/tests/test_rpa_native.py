import pytest
from qupled.native import Rpa, RpaInput


def test_rpa_properties():
    scheme = Rpa(RpaInput())
    assert hasattr(scheme, "idr")
    assert hasattr(scheme, "sdr")
    assert hasattr(scheme, "slfc")
    assert hasattr(scheme, "ssf")
    assert hasattr(scheme, "ssf_HF")
    with pytest.raises(RuntimeError) as excinfo:
        hasattr(scheme, "internal_energy")
    assert excinfo.value.args[0] == "No data to compute the internal energy"
    assert hasattr(scheme, "wvg")
    assert hasattr(scheme, "recovery")


def test_rpa_compute():
    inputs = RpaInput()
    inputs.coupling = 1.0
    inputs.degeneracy = 1.0
    inputs.theory = "RPA"
    inputs.chemical_potential = [-10, 10]
    inputs.cutoff = 10.0
    inputs.matsubara = 128
    inputs.resolution = 0.1
    inputs.integral_error = 1.0e-5
    inputs.threads = 1
    scheme = Rpa(inputs)
    scheme.compute()
    nx = scheme.wvg.size
    assert nx >= 3
    assert scheme.idr.shape[0] == nx
    assert scheme.idr.shape[1] == inputs.matsubara
    assert scheme.sdr.size == nx
    assert scheme.slfc.size == nx
    assert scheme.ssf.size == nx
    assert scheme.ssf_HF.size == nx
    assert scheme.recovery == ""
    assert scheme.rdf(scheme.wvg).size == nx
