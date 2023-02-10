from django.db import models
from django.contrib.auth.models import AbstractUser
from management.models import ApplicationExtension, ApplicationContentType
# Create your models here.


class Client(AbstractUser):
    email = models.EmailField(max_length=200, null=True, blank=True, unique=True,
                              error_messages={"unique": "Email already exists."})
    client_name = models.CharField(max_length=200, null=True, blank=True,
                                   error_messages={"unique": "Client name already exists."})
    username = models.CharField(max_length=250, null=True, blank=True, unique=True,
                                error_messages={"unique": "This username already exists."})
    client_token = models.CharField(null=True, blank=True, max_length=100, unique=True,
                                    error_messages={"unique": "Client token already exists."})
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['client_name', 'username']   # Fields that are required when creating a user from the Terminal

    def __str__(self):
        return "{client_name} - {email}".format(client_name=self.client_name, email=self.email)


class ValidatorBlock(models.Model):
    block_name = models.CharField(max_length=100, null=True, blank=True)
    block_token = models.CharField(max_length=100, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    file_threshold_size = models.DecimalField(null=False, decimal_places=2, max_digits=10, blank=False, default=0,
                                              help_text="Any file size above this threshold will be "
                                                        "rejected. Sizes are converted to KB.")
    allow_size_check = models.BooleanField(default=False)
    # Dimension = width (pixels) X height (pixels)
    # Resolution tellList of fields:s the amount of Pixels present in an Image.
    # 6000(w) X 6000(h) = 40,000 Pixels are present in the img
    # 6000 pixels in width (6000 pixels per col.) and 4000 pixels in height (4000 pixels per row).

    # Images should not have pixels lesser than the assigned value for this block in width and in height.
    image_height_dimension_threshold = models.PositiveSmallIntegerField(null=False, blank=False, default=0, help_text="image height dimension treshold will be used to validate both height.")
    image_width_dimension_threshold = models.PositiveSmallIntegerField(null=False, blank=False, default=0, help_text="image width dimension treshold will be used to validate both width.")
    allow_dimension_check = models.BooleanField(default=False)
    # Allowed extensions [png, jpeg, jpg]
    allowed_extensions = models.ManyToManyField(ApplicationExtension, help_text="List of allowed extensions")
    allow_extension_check = models.BooleanField(default=False)
    # Allowed Content-Type [ 'image/gif', 'image/jpeg', 'image/png', image/tiff, image/vnd.microsoft.icon,
    # image/x-icon, image/vnd.djvu, image/svg+xml ]
    content_type = models.ManyToManyField(ApplicationContentType,
                                          help_text="What ever content type that has been selected by the "
                                                    "client will "
                                                    "be allowed for the Image Processing of this Validator Block. "
                                                    "E.g {'jpeg': 'image/jpeg'}, "
                                                    "it means images with content type of jpeg will be acceptable.")
    allow_content_type_check = models.BooleanField(default=False)
    numb_of_images_per_process = models.PositiveSmallIntegerField(null=True, blank=True, default=1)
    allow_number_of_image_check = models.BooleanField(default=False)
    allow_blurry_images = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - {self.block_name}"
