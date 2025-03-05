#!/usr/bin/env python
# coding=utf-8
"""
Author: Liu Kun && 16031215@qq.com
Date: 2024-09-17 17:12:47
LastEditors: Liu Kun && 16031215@qq.com
LastEditTime: 2024-12-13 19:11:08
FilePath: \\Python\\My_Funcs\\OAFuncs\\oafuncs\\oa_data.py
Description:
EditPlatform: vscode
ComputerInfo: XPS 15 9510
SystemInfo: Windows 11
Python Version: 3.11
"""

import itertools
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import xarray as xr
from scipy.interpolate import griddata
import salem

__all__ = ["interp_2d", "ensure_list", "mask_shapefile"]


def ensure_list(input_data):
    """
    Ensures that the input is converted into a list.

    If the input is already a list, it returns it directly.
    If the input is a string, it wraps it in a list and returns.
    For other types of input, it converts them to a string and then wraps in a list.

    :param input_data: The input which can be a list, a string, or any other type.
    :return: A list containing the input or the string representation of the input.
    """
    if isinstance(input_data, list):
        return input_data
    elif isinstance(input_data, str):
        return [input_data]
    else:
        # For non-list and non-string inputs, convert to string and wrap in a list
        return [str(input_data)]


def interp_2d(target_x, target_y, origin_x, origin_y, data, method="linear", parallel=True):
    """
    Perform 2D interpolation on the last two dimensions of a multi-dimensional array.

    Parameters:
    - target_x (array-like): 1D array of target grid's x-coordinates.
    - target_y (array-like): 1D array of target grid's y-coordinates.
    - origin_x (array-like): 1D array of original grid's x-coordinates.
    - origin_y (array-like): 1D array of original grid's y-coordinates.
    - data (numpy.ndarray): Multi-dimensional array where the last two dimensions correspond to the original grid.
    - method (str, optional): Interpolation method, default is 'linear'. Other options include 'nearest', 'cubic', etc.
    - parallel (bool, optional): Flag to enable parallel processing. Default is True.

    Returns:
    - interpolated_data (numpy.ndarray): Interpolated data with the same leading dimensions as the input data, but with the last two dimensions corresponding to the target grid.

    Raises:
    - ValueError: If the shape of the data does not match the shape of the origin_x or origin_y grids.

    Usage:
    - Interpolate a 2D array:
        result = interp_2d(target_x, target_y, origin_x, origin_y, data_2d)
    - Interpolate a 3D array (where the last two dimensions are spatial):
        result = interp_2d(target_x, target_y, origin_x, origin_y, data_3d)
    - Interpolate a 4D array (where the last two dimensions are spatial):
        result = interp_2d(target_x, target_y, origin_x, origin_y, data_4d)
    """

    def interp_single(data_slice, target_points, origin_points, method):
        return griddata(origin_points, data_slice.ravel(), target_points, method=method).reshape(target_y.shape)

    # 确保目标网格和初始网格都是二维的
    if len(target_y.shape) == 1:
        target_x, target_y = np.meshgrid(target_x, target_y)
    if len(origin_y.shape) == 1:
        origin_x, origin_y = np.meshgrid(origin_x, origin_y)

    # 根据经纬度网格判断输入数据的形状是否匹配
    if origin_x.shape != data.shape[-2:] or origin_y.shape != data.shape[-2:]:
        raise ValueError("Shape of data does not match shape of origin_x or origin_y.")

    # 创建网格和展平数据
    target_x, target_y = np.array(target_x), np.array(target_y)
    origin_x, origin_y = np.array(origin_x), np.array(origin_y)
    target_points = np.column_stack((target_y.ravel(), target_x.ravel()))
    origin_points = np.column_stack((origin_y.ravel(), origin_x.ravel()))

    # 根据是否并行选择不同的执行方式
    if parallel:
        with ThreadPoolExecutor(max_workers=mp.cpu_count() - 2) as executor:
            if len(data.shape) == 2:
                interpolated_data = list(executor.map(interp_single, [data], [target_points], [origin_points], [method]))
            elif len(data.shape) == 3:
                interpolated_data = list(executor.map(interp_single, [data[i] for i in range(data.shape[0])], [target_points] * data.shape[0], [origin_points] * data.shape[0], [method] * data.shape[0]))
            elif len(data.shape) == 4:
                index_combinations = list(itertools.product(range(data.shape[0]), range(data.shape[1])))
                interpolated_data = list(executor.map(interp_single, [data[i, j] for i, j in index_combinations], [target_points] * len(index_combinations), [origin_points] * len(index_combinations), [method] * len(index_combinations)))
                interpolated_data = np.array(interpolated_data).reshape(data.shape[0], data.shape[1], *target_y.shape)
    else:
        if len(data.shape) == 2:
            interpolated_data = interp_single(data, target_points, origin_points, method)
        elif len(data.shape) == 3:
            interpolated_data = np.stack([interp_single(data[i], target_points, origin_points, method) for i in range(data.shape[0])])
        elif len(data.shape) == 4:
            interpolated_data = np.stack([np.stack([interp_single(data[i, j], target_points, origin_points, method) for j in range(data.shape[1])]) for i in range(data.shape[0])])

    return np.squeeze(np.array(interpolated_data))


def mask_shapefile(data: np.ndarray, lons: np.ndarray, lats: np.ndarray, shapefile_path: str) -> xr.DataArray:
    """
    Masks a 2D data array using a shapefile.

    Parameters:
    - data: 2D numpy array of data to be masked.
    - lons: 1D numpy array of longitudes.
    - lats: 1D numpy array of latitudes.
    - shapefile_path: Path to the shapefile used for masking.

    Returns:
    - Masked xarray DataArray.
    """
    """
    https://cloud.tencent.com/developer/article/1701896
    """
    try:
        # import geopandas as gpd
        # shp_f = gpd.read_file(shapefile_path)
        shp_f = salem.read_shapefile(shapefile_path)
        data_da = xr.DataArray(data, coords=[("latitude", lats), ("longitude", lons)])
        masked_data = data_da.salem.roi(shape=shp_f)
        return masked_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    pass
    """ import time

    import matplotlib.pyplot as plt

    # 测试数据
    origin_x = np.linspace(0, 10, 11)
    origin_y = np.linspace(0, 10, 11)
    target_x = np.linspace(0, 10, 101)
    target_y = np.linspace(0, 10, 101)
    data = np.random.rand(11, 11)

    # 高维插值
    origin_x = np.linspace(0, 10, 11)
    origin_y = np.linspace(0, 10, 11)
    target_x = np.linspace(0, 10, 101)
    target_y = np.linspace(0, 10, 101)
    data = np.random.rand(10, 10, 11, 11)

    start = time.time()
    interpolated_data = interp_2d(target_x, target_y, origin_x, origin_y, data, parallel=False)
    print(f"Interpolation time: {time.time()-start:.2f}s")

    print(interpolated_data.shape)

    # 高维插值多线程
    start = time.time()
    interpolated_data = interp_2d(target_x, target_y, origin_x, origin_y, data)
    print(f"Interpolation time: {time.time()-start:.2f}s")

    print(interpolated_data.shape)
    print(interpolated_data[0, 0, :, :].shape)
    plt.figure()
    plt.contourf(target_x, target_y, interpolated_data[0, 0, :, :])
    plt.colorbar()
    plt.show() """
