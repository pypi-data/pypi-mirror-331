"""
ImageSer

This module provides two classes for generating image path sequences:

Classes:
    RepeatingImageSer:
        Creates a repeating pattern of image paths.
    
    GrowingImageSer:
        Generates a growing pattern of image paths, where each stage increases in repetition.

Methods:
    __init__(imgs_path, t):
        Initializes the instance with a list of image paths and a repeat factor.
    
    __repr__() -> str:
        Returns a string representation of the object.
    
    __len__() -> int:
        Returns the length of the image series.
    
    FullSer():
        Displays all images in the generated series.
"""
from PIL import Image #type:ignore

class RepeatingImageSer:
    """
    A class to create a repeating pattern of image paths.

    Attributes:
        ser (list): A list containing repeated image paths.
    """

    def __init__(self, imgs_path, t):
        """
        Initializes the RepeatingImageSer class.

        Args:
            imgs_path (list): A list of image paths.
            t (int): The number of times to repeat the list.

        Raises:
            TypeError: If imgs_path is not a list.
        """
        if not isinstance(imgs_path, list):
            raise TypeError("The imgs_path should be a list")

        self.ser = imgs_path * t  # Repeat the elements properly

    def __repr__(self):
        """
        Returns a string representation of the object.
        """
        return "Provide any img_path and make a repeating pattern series"
    
    def __len__(self):
        """
        Returns the length of the series.
        """
        return len(self.ser)
    
    def FullSer(self):
        """
        Displays all images in the series.
        """
        for path in self.ser:
            img = Image.open(path)
            img.show()

class GrowingImageSer:
    """
    A class to create a growing pattern of image paths.

    Attributes:
        ser (list): A list containing the growing sequence of image paths.
        r (int): The repetition factor for each stage.
        n (int): The number of growth stages.
    """

    def __init__(self, imgs_path, t, r):
        """
        Initializes the GrowingImageSer class.

        Args:
            imgs_path (list): A list of image paths.
            t (int): The number of growth stages.
            r (int): The factor by which each stage grows.
        """
        if not isinstance(imgs_path, list):
            raise TypeError("The imgs_path should be a list")

        self.r = r
        self.n = t
        self.ser = [imgs_path]  # Start with the initial list

        # Generate the growing series
        for _ in range(self.n - 1):
            tempser = []
            for path in self.ser[-1]:  # Take the last generated sequence
                tempser.extend([path] * r)  # Repeat each path r times
            self.ser.append(tempser)

    def __repr__(self):
        """
        Returns a string representation of the object.
        """
        return "Provide any img paths and make it a GrowingImageSer"
    
    def __len__(self):
        """
        Returns the length of the series.
        """
        return len(self.ser)
    
    def FullSer(self):
        """
        Displays all images in the series.
        """
        for paths in self.ser:
            for path in paths:
                img = Image.open(path)
                img.show()
