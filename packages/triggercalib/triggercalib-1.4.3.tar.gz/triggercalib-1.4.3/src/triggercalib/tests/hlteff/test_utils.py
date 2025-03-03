###############################################################################
# (c) Copyright 2024-2025 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

from ctypes import c_double
import ROOT as R

R.gROOT.SetBatch(True)


def test_bins_io_json(example_file_hlteff):
    import json
    from triggercalib import HltEff

    tree, path = example_file_hlteff

    h1 = HltEff(
        "test_write_bins",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        expert_mode=True,
        lazy=True,
    )
    h1.set_binning(
        {"observ1": {"label": "Observable 1", "bins": [5, 0, 8]}},
        compute_bins=True,
        bin_cut="discrim > 5100 && discrim < 5300 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )
    h1.write_bins("results/test_bins_io_binning.json")

    # Read in binning scheme
    with open("results/test_bins_io_binning.json", "r") as binning_file:
        binning = json.load(binning_file)

    h2 = HltEff(
        "test_read_bins",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        binning=binning,
        expert_mode=True,
        lazy=True,
    )

    assert h1.binning_scheme == h2.binning_scheme


def test_bins_io_yaml(example_file_hlteff):
    import yaml
    from triggercalib import HltEff

    tree, path = example_file_hlteff

    h1 = HltEff(
        "test_write_bins",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        expert_mode=True,
        lazy=True,
    )
    h1.set_binning(
        {"observ1": {"label": "Observable 1", "bins": [5, 0, 8]}},
        compute_bins=True,
        bin_cut="discrim > 5100 && discrim < 5300 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )
    h1.write_bins("results/test_bins_io_binning.yaml")

    # Read in binning scheme
    with open("results/test_bins_io_binning.yaml", "r") as binning_file:
        binning = yaml.safe_load(binning_file)

    h2 = HltEff(
        "test_read_bins",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        binning=binning,
        expert_mode=True,
        lazy=True,
    )

    assert h1.binning_scheme == h2.binning_scheme


def test_bins_io_yaml(example_file_hlteff):
    import yaml
    from triggercalib import HltEff

    tree, path = example_file_hlteff

    h1 = HltEff(
        "test_write_bins",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        expert_mode=True,
        lazy=True,
    )
    h1.set_binning(
        {"observ1": {"label": "Observable 1", "bins": [5, 0, 8]}},
        compute_bins=True,
        bin_cut="discrim > 5100 && discrim < 5300 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )
    h1.write_bins("results/test_bins_io_binning.yaml")

    # Read in binning scheme
    with open("results/test_bins_io_binning.yaml", "r") as binning_file:
        binning = yaml.safe_load(binning_file)

    h2 = HltEff(
        "test_read_bins",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        binning=binning,
        expert_mode=True,
        lazy=True,
    )

    assert h1.binning_scheme == h2.binning_scheme


def test_conversion_to_th1(example_file_hlteff):
    from triggercalib import HltEff
    from triggercalib.utils.helpers import tgraph_to_np, th_to_np

    tree, path = example_file_hlteff

    hlteff = HltEff(
        "test_conversion_to_th1",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        expert_mode=True,
        lazy=True,
    )
    hlteff.set_binning(
        {
            "observ1": {"label": "Observable 1", "bins": [4, 0, 8]},
        },
        compute_bins=True,
        bin_cut="discrim > 5100 && discrim < 5300 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )

    hlteff.counts("conversion_th1")
    hlteff.efficiencies("conversion_th1")

    # Test th_to_np
    xvals, yvals, xerrs, yerrs = th_to_np(
        hlteff["counts"]["conversion_th1_trig_count_observ1"]
    )

    hist_tgraph = hlteff.get_eff("conversion_th1_trig_efficiency_observ1", as_th=False)
    hist_th = hlteff.get_eff("conversion_th1_trig_efficiency_observ1", as_th=True)

    # Sum values/errors in tgraph
    tgraph_sum_vals = 0
    tgraph_sum_errs = 0

    # Sum values/errors in th1
    th_sum_vals = 0
    th_sum_errs = 0

    x = c_double(0)
    y = c_double(0)
    for point in range(hist_tgraph.GetN()):
        hist_tgraph.GetPoint(point, x, y)
        tgraph_sum_vals += y.value
        tgraph_sum_errs += hist_tgraph.GetErrorY(point)

        bin_n = hist_th.FindBin(x)
        th_sum_vals += hist_th.GetBinContent(bin_n)
        th_sum_errs += hist_th.GetBinError(bin_n)

    assert (
        tgraph_sum_vals == th_sum_vals
        and th_sum_vals == hist_th.GetSumOfWeights()
        and tgraph_sum_errs == th_sum_errs
    )

    # Test tgraph_to_np
    xvals, yvals, (xlow_errs, xhigh_errs), (ylow_errs, yhigh_errs) = tgraph_to_np(
        hist_tgraph
    )


def test_conversion_to_th2(example_file_hlteff):
    from triggercalib import HltEff

    tree, path = example_file_hlteff

    hlteff = HltEff(
        "test_conversion_to_th2",
        tis="Hlt1DummyOne",
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        expert_mode=True,
        lazy=True,
    )
    hlteff.set_binning(
        {
            "observ1": {"label": "Observable 1", "bins": [4, 0, 8]},
            "observ2": {"label": "Observable 2", "bins": [4, -18, 12]},
        },
        compute_bins=True,
        bin_cut="discrim > 5100 && discrim < 5300 && P_Hlt1DummyOneDecision_TIS && P_Hlt1DummyOneDecision_TOS",
    )
    hlteff.counts("conversion_th2")
    hlteff.efficiencies("conversion_th2")

    hist_tgraph = hlteff.get_eff(
        "conversion_th2_trig_efficiency_observ1_observ2", as_th=False
    )
    hist_th = hlteff.get_eff(
        "conversion_th2_trig_efficiency_observ1_observ2", as_th=True
    )

    # Sum values/errors in tgraph
    tgraph_sum_vals = 0
    tgraph_sum_errs = 0

    # Sum values/errors in th1
    th_sum_vals = 0
    th_sum_errs = 0

    x = c_double(0)
    y = c_double(0)
    z = c_double(0)
    for point in range(hist_tgraph.GetN()):
        hist_tgraph.GetPoint(point, x, y, z)
        tgraph_sum_vals += z.value
        tgraph_sum_errs += hist_tgraph.GetErrorZ(point)

        bin_n = hist_th.FindBin(x, y)
        th_sum_vals += hist_th.GetBinContent(bin_n)
        th_sum_errs += hist_th.GetBinError(bin_n)


def test_regex(example_file_hlteff):
    from triggercalib import HltEff

    tree, path = example_file_hlteff

    hlteff_regex = HltEff(
        "test_regex",
        tis="Hlt1.*",
        tos="Hlt1.*One",
        particle="P",
        path=f"{path}:{tree}",
        expert_mode=True,
        lazy=True,
    )

    hlteff_explicit = HltEff(
        "test_explicit",
        tis=["Hlt1DummyOne", "Hlt1DummyTwo"],
        tos="Hlt1DummyOne",
        particle="P",
        path=f"{path}:{tree}",
        expert_mode=True,
        lazy=True,
    )

    assert hlteff_regex.tis == hlteff_explicit.tis
    assert hlteff_regex.tos == hlteff_explicit.tos
