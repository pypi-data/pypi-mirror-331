import numpy as np
from scipy.integrate import cumulative_trapezoid as cumtrapz


def acceleration_to_velocity_time(a, t):
    """
    Переводит виброускорение в виброскорость во временной области.

    Параметры:
    a : array-like
        Массив значений виброускорения.
    t : array-like
        Массив значений времени.

    Возвращает:
    v : array-like
        Массив значений виброскорости.
    """
    v = cumtrapz(a, t, initial=0)
    return v


def velocity_to_displacement_time(v, t):
    """
    Переводит виброскорость в виброперемещение во временной области.

    Параметры:
    v : array-like
        Массив значений виброскорости.
    t : array-like
        Массив значений времени.

    Возвращает:
    x : array-like
        Массив значений виброперемещения.
    """
    x = cumtrapz(v, t, initial=0)
    return x


def acceleration_to_displacement_time(a, t):
    """
    Переводит виброускорение в виброперемещение во временной области.

    Параметры:
    a : array-like
        Массив значений виброускорения.
    t : array-like
        Массив значений времени.

    Возвращает:
    x : array-like
        Массив значений виброперемещения.
    """
    v = acceleration_to_velocity_time(a, t)
    x = velocity_to_displacement_time(v, t)
    return x


def acceleration_to_velocity_spectrum(A, frequencies):
    """
    Переводит спектр виброускорения в спектр виброскорости.

    Параметры:
    A : array-like
        Массив значений спектра виброускорения.
    frequencies : array-like
        Массив частот, соответствующих значениям спектра.

    Возвращает:
    V : array-like
        Массив значений спектра виброскорости.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        V = A / (2 * np.pi * frequencies)
    V[frequencies == 0] = 0  # Убираем нулевую частоту
    return V


def velocity_to_displacement_spectrum(V, frequencies):
    """
    Переводит спектр виброскорости в спектр виброперемещения.

    Параметры:
    V : array-like
        Массив значений спектра виброскорости.
    frequencies : array-like
        Массив частот, соответствующих значениям спектра.

    Возвращает:
    X : array-like
        Массив значений спектра виброперемещения.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        X = V / (2 * np.pi * frequencies)
    X[frequencies == 0] = 0  # Убираем нулевую частоту
    return X


def acceleration_to_displacement_spectrum(A, frequencies):
    """
    Переводит спектр виброускорения в спектр виброперемещения.

    Параметры:
    A : array-like
        Массив значений спектра виброускорения.
    frequencies : array-like
        Массив частот, соответствующих значениям спектра.

    Возвращает:
    X : array-like
        Массив значений спектра виброперемещения.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        X = A / (2 * np.pi * frequencies) ** 2
    X[frequencies == 0] = 0  # Убираем нулевую частоту
    return X


def acceleration_to_decibels(acceleration_spectrum, reference=1e-6):
    """
    Преобразует спектр виброускорения в спектр в децибелах.

    :param acceleration_spectrum: Массив с данными спектра виброускорения (м/с^2).
    :param reference: Опорное значение для расчета децибел (по умолчанию 1e-6 м/с^2).
    :return: Спектр виброускорения в децибелах.
    """
    # Преобразуем ускорение в децибелы
    decibel_spectrum = 20 * np.log10(np.abs(acceleration_spectrum) / reference)

    return decibel_spectrum