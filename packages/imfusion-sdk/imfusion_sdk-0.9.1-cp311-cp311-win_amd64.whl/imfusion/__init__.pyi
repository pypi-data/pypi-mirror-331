"""

imfusion - ImFusion SDK for Medical Imaging
===========================================

This module provides Python bindings for the C++ ImFusion libraries.
"""
from __future__ import annotations
from functools import wraps
from imfusion.Algorithm import Algorithm
from imfusion._bindings import AlgorithmExecutionError
from imfusion._bindings import Annotation
from imfusion._bindings import AnnotationModel
from imfusion._bindings import ApplicationController
from imfusion._bindings import BaseAlgorithm
from imfusion._bindings import Configurable
from imfusion._bindings import ConsoleController
from imfusion._bindings import CroppingMask
from imfusion._bindings import Data
from imfusion._bindings import DataComponent
from imfusion._bindings import DataComponentBase
from imfusion._bindings import DataComponentList
from imfusion._bindings import DataGroup
from imfusion._bindings import DataList
from imfusion._bindings import DataModel
from imfusion._bindings import DataSourceComponent
from imfusion._bindings import DatasetLicenseComponent
from imfusion._bindings import Deformation
from imfusion._bindings import Display
from imfusion._bindings import DisplayOptions2d
from imfusion._bindings import DisplayOptions3d
from imfusion._bindings import ExplicitIntensityMask
from imfusion._bindings import ExplicitMask
from imfusion._bindings import FileNotFoundError
from imfusion._bindings import FrameworkInfo
from imfusion._bindings import FreeFormDeformation
from imfusion._bindings import GlPlatformInfo
from imfusion._bindings import IOError
from imfusion._bindings import ImageDescriptor
from imfusion._bindings import ImageDescriptorWorld
from imfusion._bindings import ImageInfoDataComponent
from imfusion._bindings import ImageResamplingAlgorithm
from imfusion._bindings import ImageView2D
from imfusion._bindings import ImageView3D
from imfusion._bindings import IncompatibleError
from imfusion._bindings import IntensityMask
from imfusion._bindings import InterpolationMode
from imfusion._bindings import LabelDataComponent
from imfusion._bindings import LayoutMode
from imfusion._bindings import LicenseInfo
from imfusion._bindings import Mask
from imfusion._bindings import MemImage
from imfusion._bindings import Mesh
from imfusion._bindings import MissingLicenseError
from imfusion._bindings import Optimizer
from imfusion._bindings import PaddingMode
from imfusion._bindings import ParametricDeformation
from imfusion._bindings import PixelType
from imfusion._bindings import PluginInfo
from imfusion._bindings import PointCloud
from imfusion._bindings import Properties
from imfusion._bindings import RealWorldMappingDataComponent
from imfusion._bindings import ReductionMode
from imfusion._bindings import Selection
from imfusion._bindings import SharedImage
from imfusion._bindings import SharedImageSet
from imfusion._bindings import SignalConnection
from imfusion._bindings import SkippingMask
from imfusion._bindings import SpacingMode
from imfusion._bindings import TrackedSharedImageSet
from imfusion._bindings import TrackerID
from imfusion._bindings import TrackingSequence
from imfusion._bindings import TransformationStashDataComponent
from imfusion._bindings import View
from imfusion._bindings import VisualizerHandle
from imfusion._bindings import VitalsDataComponent
from imfusion._bindings import _register_algorithm
from imfusion._bindings import algorithmName
from imfusion._bindings import algorithm_properties
from imfusion._bindings import auto_window
from imfusion._bindings import available_algorithms
from imfusion._bindings import available_data_components
from imfusion._bindings import close_viewers
from imfusion._bindings import create_algorithm
from imfusion._bindings import create_data_component
from imfusion._bindings import deinit
from imfusion._bindings import execute_algorithm
from imfusion._bindings import gpu_info
from imfusion._bindings import has_gl_context
from imfusion._bindings import info
from imfusion._bindings import init
from imfusion._bindings import io
from imfusion._bindings import list_viewers
from imfusion._bindings import load
from imfusion._bindings import load_plugin
from imfusion._bindings import load_plugins
from imfusion._bindings import log_debug
from imfusion._bindings import log_error
from imfusion._bindings import log_fatal
from imfusion._bindings import log_info
from imfusion._bindings import log_level
from imfusion._bindings import log_trace
from imfusion._bindings import log_warn
from imfusion._bindings import mesh
from imfusion._bindings import open
from imfusion._bindings import open_in_suite
from imfusion._bindings import py_doc_url
from imfusion._bindings import save
from imfusion._bindings import set_log_level
from imfusion._bindings import show
from imfusion._bindings import transfer_logging_to_python
from imfusion._bindings import unregister_algorithm
import importlib as importlib
import inspect as inspect
import numpy as numpy
import os as os
import sys as sys
import warnings as warnings
from . import _bindings
from . import _devenv
from . import dicom
from . import imagemath
from . import machinelearning
from . import registration
__all__ = ['Algorithm', 'AlgorithmExecutionError', 'Annotation', 'AnnotationModel', 'ApplicationController', 'BaseAlgorithm', 'Configurable', 'ConsoleController', 'CroppingMask', 'Data', 'DataComponent', 'DataComponentBase', 'DataComponentList', 'DataGroup', 'DataList', 'DataModel', 'DataSourceComponent', 'DatasetLicenseComponent', 'Deformation', 'Display', 'DisplayOptions2d', 'DisplayOptions3d', 'ExplicitIntensityMask', 'ExplicitMask', 'FileNotFoundError', 'FrameworkInfo', 'FreeFormDeformation', 'GlPlatformInfo', 'IOError', 'ImageDescriptor', 'ImageDescriptorWorld', 'ImageInfoDataComponent', 'ImageResamplingAlgorithm', 'ImageView2D', 'ImageView3D', 'IncompatibleError', 'IntensityMask', 'InterpolationMode', 'LabelDataComponent', 'LayoutMode', 'LicenseInfo', 'Mask', 'MemImage', 'Mesh', 'MissingLicenseError', 'Optimizer', 'PaddingMode', 'ParametricDeformation', 'PixelType', 'PluginInfo', 'PointCloud', 'Properties', 'RealWorldMappingDataComponent', 'ReductionMode', 'ReferenceImageDataComponent', 'RegionOfInterest', 'Selection', 'SharedImage', 'SharedImageSet', 'SignalConnection', 'SkippingMask', 'SpacingMode', 'TrackedSharedImageSet', 'TrackerID', 'TrackingSequence', 'TransformationStashDataComponent', 'View', 'VisualizerHandle', 'VitalsDataComponent', 'algorithmName', 'algorithm_properties', 'app', 'auto_window', 'available_algorithms', 'available_data_components', 'close_viewers', 'create_algorithm', 'create_data_component', 'deinit', 'dicom', 'execute_algorithm', 'gpu_info', 'has_gl_context', 'imagemath', 'importlib', 'info', 'init', 'inspect', 'io', 'keep_data_alive', 'list_viewers', 'load', 'load_plugin', 'load_plugins', 'log_debug', 'log_error', 'log_fatal', 'log_info', 'log_level', 'log_trace', 'log_warn', 'machinelearning', 'mesh', 'name', 'numpy', 'open', 'open_in_suite', 'os', 'py_doc_url', 'register_algorithm', 'registration', 'save', 'set_log_level', 'show', 'sys', 'to_wrap', 'transfer_logging_to_python', 'try_import_imfusion_plugin', 'unregister_algorithm', 'warnings', 'wraps']
class ReferenceImageDataComponent(_bindings.DataComponentBase):
    reference: _bindings.SharedImageSet
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class RegionOfInterest:
    offset: numpy.ndarray[numpy.int32[3, 1]]
    size: numpy.ndarray[numpy.int32[3, 1]]
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, arg0: numpy.ndarray[numpy.int32[3, 1]], arg1: numpy.ndarray[numpy.int32[3, 1]]) -> None:
        ...
def __SIS_apply_shift_and_scale(self, arr):
    """
    
        Return a copy of the array with storage values converted to original values.
    
        :param self: instance of a SharedImageSet which provides shift and scale
        :param arr: array to be converted from storage values into original values
        :return: numpy.ndarray
        
    """
def __SIS_array(self, **kwargs):
    """
    
        Convenience method for reading a SharedImageSet as storage values, without shift and scale considered.
    
        :param self: instance of a SharedImageSet
        :return: numpy.ndarray
        
    """
def __SIS_assign_array(self, arr):
    """
    
        Copies the contents of arr to the MemImage.
        Automatically calls setDirtyMem.
        
    """
def __SIS_convert_images_into_numpy_array(self):
    """
    
        Convenience method for reading a SharedImageSet as original values, with shift and scale already applied.
    
        :param self: instance of a SharedImageSet
        :return: numpy.ndarray
        
    """
def __SI_assign_array(self, arr, casting = 'same_kind'):
    """
    
        Copies the contents of arr to the SharedImage.
        Automatically calls setDirtyMem.
    
        The casting parameters behaves like numpy.copyto.
        
    """
def __apply_shift_and_scale(self, arr):
    """
    
        Return a copy of the array with storage values converted to original values.
        The dtype of the returned array is always DOUBLE.
        
    """
def __best_dtype(dtype_list: typing.List[numpy.dtype]) -> numpy.dtype:
    """
    
        Helper function that returns a dtype that allows to represent the values in the range defined
        by the union of the ranges determined by the input dtypes.
    
        The max integer returned by this function has 32 bits: any integer with more bits will determine
        a double dtype.
    
        :param dtype_list: a list of numpy.dtypes, it must have size at least 1 as it is not checked.
        :return: the dtype that allows to represent all the values represented by the input dtypes.
        
    """
def __cleanup():
    """
    
        Deletes the ApplicationController on exit and calls deinit().
        This assures the OpenGL context is cleaned-up correctly.
        
    """
def __convert_image_into_numpy_array(self):
    """
    
        Convenience method for converting a MemImage or a SharedImage into a newly created numpy array with scale and shift
        already applied.
    
        Shift and scale may determine a complex change of pixel type prior the conversion into numpy array:
    
        - as a first rule, even if the type of shift and scale is float, they will still be considered as integers if
          they are representing integers (e.g. a shift of 2.000 will be treated as 2);
        - if shift and scale are such that the pixel values range (determined by the pixel_type) would not be fitting into
          the pixel_type, e.g. a negative pixel value but the type is unsigned, then the pixel_type will be promoted into
          a signed type if possible, otherwise into a single precision floating point type;
        - if shift and scale are such that the pixel values range (determined by the pixel_type) would be fitting into a
          demoted pixel_type, e.g. the type is signed but the range of pixel values is unsigned, then the pixel_type
          will be demoted;
        - if shift and scale do not certainly determine that all the possible pixel values (in the range determined by the
          pixel_type) would become integers, then the pixel_type will be promoted into a single precision floating point
          type.
        - in any case, the returned numpy array will be returned with type up to 32-bit integers. If the integer type
          would require more bits, then the resulting pixel_type will be DOUBLE.
    
        :param self: instance of a MemImage or of a SharedImage
        :return: numpy.ndarray
        
    """
def keep_data_alive(cls):
    ...
def register_algorithm(id, name, cls):
    """
    
        Register an Algorithm to the framework.
    
        The Algorithm will be accessible through the given id.
        If the id is already used, the registration will fail.
    
        cls must derive from Algorithm otherwise a TypeError is
        raised.
        
    """
def try_import_imfusion_plugin(plugin: str) -> None:
    ...
app = None
name: str = 'Algorithm'
to_wrap: list = ['BaseAlgorithm', 'ImageResamplingAlgorithm', 'Algorithm']
