import numpy as np
from scipy.signal import hilbert

from . import compute_amplitude_spectrum
from .preprocessing import filter_signal, apply_window


def compute_envelope_spectrum(signal, sampling_rate, lowcut, highcut, window_type=None):
    """
    Вычисляет спектр огибающей сигнала.

    :param signal: Входной сигнал.
    :param sampling_rate: Частота дискретизации.
    :param lowcut: Нижняя граница полосы фильтра (Гц).
    :param highcut: Верхняя граница полосы фильтра (Гц).
    :param window_type: Тип окна (None, 'hann', 'hamming', 'blackman').
    :return: Кортеж (frequencies, envelope_spectrum), где:
             - frequencies: Массив частот (Гц).
             - envelope_spectrum: Спектр огибающей.
    """
    # Применяем полосовой фильтр
    filtered_signal = filter_signal(signal, (lowcut, highcut), sampling_rate, 'bandpass')

    # Накладываем окно (если указано)
    if window_type is not None:
        filtered_signal = apply_window(filtered_signal, window_type)

    # Вычисляем огибающую с помощью преобразования Гильберта
    analytic_signal = hilbert(filtered_signal)
    envelope = np.abs(analytic_signal)

    # Вычисляем спектр огибающей
    frequencies, spectrum = compute_amplitude_spectrum(envelope, sampling_rate)

    return frequencies, spectrum