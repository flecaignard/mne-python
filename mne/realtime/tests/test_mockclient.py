import os.path as op

import mne
from mne import Epochs, read_events
from mne.realtime import MockRtClient, RtEpochs
from mne.datasets import sample
from mne.event import find_events

from nose.tools import assert_true
from numpy.testing import assert_array_equal

base_dir = op.join(op.dirname(__file__), '..', '..', 'fiff', 'tests', 'data')
raw_fname = op.join(base_dir, 'test_raw.fif')
event_name = op.join(base_dir, 'test-eve.fif')


def test_mockclient():
    """Test the RtMockClient
    """
    raw = mne.fiff.Raw(raw_fname, preload=True, verbose=False)

    events = read_events(event_name)

    picks = mne.fiff.pick_types(raw.info, meg='grad', eeg=False, eog=True,
                                stim=True, exclude=raw.info['bads'])
    event_id, tmin, tmax = 1, -0.2, 0.5

    epochs = Epochs(raw, events[:7], event_id=event_id, tmin=tmin, tmax=tmax,
                    picks=picks, baseline=(None, 0), preload=True)
    data = epochs.get_data()

    rt_client = MockRtClient(raw)
    rt_epochs = RtEpochs(rt_client, event_id, tmin, tmax, picks=picks)

    rt_epochs.start()
    rt_client.send_data(rt_epochs, picks, tmin=0, tmax=10, buffer_size=1000)

    rt_data = rt_epochs.get_data()

    assert_true(rt_data.shape == data.shape)
    assert_array_equal(rt_data, data)


def test_fakebrainresponse():
    """Test the fakebrainresponse
    """
    data_path = sample.data_path()
    raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
    raw_sample = mne.fiff.Raw(raw_fname, preload=True)

    event_id, tmin, tmax = 2, -0.1, 0.3

    events_sample = find_events(raw_sample, verbose=None, output='onset',
                                consecutive='increasing')

    epochs = Epochs(raw_sample, events_sample[:3], event_id=event_id,
                    tmin=tmin, tmax=tmax, picks=picks, baseline=None,
                    preload=True, proj=False)

    data = epochs.get_data()[0, :, :]

    rt_client = MockRtClient(raw_sample)
    rt_data = rt_client.fake_data(event_id=event_id, tmin=tmin,
                                  tmax=tmax, picks=picks)

    assert_array_equal(rt_data, data)
