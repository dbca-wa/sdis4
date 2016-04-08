# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager, Group)
from django.core import validators
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

class UserManager(BaseUserManager):
#    def __init__(self):
#        super(BaseUserManager, self).__init__()
#        self.model = get_user_model()

    def get_short_name(self):
        return self.username

    def _create_user(self, username, password, is_staff, is_superuser,
                     **extra_fields):
        now = timezone.now()
        user = self.model(username=username, is_staff=is_staff,
                          is_active=True, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields = extra_fields or {}
        extra_fields.setdefault('email', email)
        return self._create_user(username, password, True, False,
                                 **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True,
                                 **extra_fields)

@python_2_unicode_compatible
class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom user model for SDIS.

    Mostly intended to make profile modification
    simpler and less "broken" (seeing a lot of "create profile if it doesn't
    exist") comments littered throughout the code.

    A user can have contact details, affiliations, research profiles and
    publications.

    Users can be:

    * Internal person
    * Internal group
    * External person
    * External group

    Title and affiliation are shown for every user type if given.
    """

    # name = models.CharField(_("Name of User"), blank=True, max_length=255)
    username = models.CharField(
        _('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. '
                    'Letters, digits and @/./+/-/_ only.'),
        validators=[validators.RegexValidator(r'^[\w.@+-]+$',
                    _('Enter a valid username.'), 'invalid')])

    # Name --------------------------------------------------------------------#
    title = models.CharField(
        # _('title'),
        max_length=30,
        null=True, blank=True,
        verbose_name=_("Academic Title"),
        help_text=_("Optional academic title, shown in team lists only if "
                    "supplied, and only for external team members."))

    first_name = models.CharField(
        # _('first name'),
        max_length=100,
        null=True, blank=True,
        verbose_name=_("First Name"),
        help_text=_("First name or given name."))

    # middle initials should just be called initials, at least label as such:
    middle_initials = models.CharField(
        # _('middle initials'),
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Initials"),
        help_text=_("Initials of first and middle names. Will be used in "
                    "team lists with abbreviated names."))

    last_name = models.CharField(
        # _('last name'),
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Last Name"),
        help_text=_("Last name or surname."))

    is_group = models.BooleanField(
        # _('Is a group'),
        default=False,
        verbose_name=_("Show as Group"),
        help_text=_("Whether this profile refers to a group, rather than "
                    "a natural person. Groups are referred to with their "
                    "group name, whereas first and last name refer to the "
                    "group's contact person."))

    group_name = models.CharField(
        # _('Group name'),
        max_length=200,
        null=True, blank=True,
        verbose_name=_("Group name"),
        help_text=_("Group name, if this profile is not a natural person. "
                    "E.g., 'Goldfields Regional Office'."))

    affiliation = models.CharField(
        # _('Affiliation'),
        max_length=200,
        null=True, blank=True,
        verbose_name=_("Affiliation"),
        help_text=_("Optional affiliation, not required for DPaW. "
                    "If provided, the affiliation will be appended to the "
                    "person or group name in parentheses."))

    # Contact details ---------------------------------------------------------#
    image = models.ImageField(
        upload_to="profiles", null=True, blank=True,
        help_text=_("If you wish, provide us with a face to the name!"))

    email = models.EmailField(_('email address'), null=True, blank=True)

    phone = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name=_("Primary Phone number"),
        help_text=_("The primary phone number during work hours."))

    phone_alt = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name=_("Alternative Phone number"),
        help_text=_("An alternative phone number during work hours."))

    fax = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name=_("Fax number"),
        help_text=_("The fax number."))

    # Affiliation: spatial, organizational ------------------------------------#
    # program = models.ForeignKey(
    #     Program, blank=True, null=True,  # optional for migrations
    #     help_text=_("The main Science and Conservation Division Program "
    #     "affilitation."))
    # work_center = models.ForeignKey(
    #     WorkCenter, null=True, blank=True,
    #     help_text=_("The work center where most time is spent. Staff only."))

    # Academic profile --------------------------------------------------------#
    profile_text = models.TextField(
        blank=True, null=True,
        help_text=_("A profile text for the staff members, roughly three "
                    "paragraphs long."))

    expertise = models.TextField(
        blank=True, null=True,
        help_text=_("A bullet point list of skills and expertise."))

    curriculum_vitae = models.TextField(
        blank=True, null=True,
        help_text=_("A brief curriculum vitae of academic qualifications and "
                    "professional memberships."))

    projects = models.TextField(
        blank=True, null=True,
        verbose_name=_("Projects outside SDIS"),
        help_text=_("Tell us about projects outside SDIS you are involved in."))

    # Publications ------------------------------------------------------------#
    # Publications should be models in their own module really
    author_code = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name=_("Author code"),
        help_text=_("The author code links users to their publications. "
                    "Staff only."))

    publications_staff = models.TextField(
        blank=True, null=True,
        verbose_name=_("Staff publications"),
        help_text=_("A list of publications produced for the Department. "
                    "Staff only."))

    publications_other = models.TextField(
        blank=True, null=True,
        verbose_name=_("Other publications"),
        help_text=_("A list of publications produced under external "
                    "affiliation, in press or otherwise unregistered as "
                    "staff publication."))

    # Administrative details --------------------------------------------------#
    is_staff = models.BooleanField(
        _('staff status'), default=True,
        help_text=_("Designates whether the user can log into this admin site."))

    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))

    is_external = models.BooleanField(
        default=False,
        verbose_name=_("External to DPaW"),
        help_text=_("Is the user external to DPaW?"))

    agreed = models.BooleanField(
        default=False, editable=False,
        verbose_name=_("Agreed to the Terms and Conditions"),
        help_text=_("Has the user agreed to SDIS' Terms and Conditions?"))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    DEFAULT_GROUP = 'Users'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

        def get_absolute_url(self):
            return reverse('users:detail', kwargs={'username': self.username})

    #--------------------------------------------------------------------------#
    # Names
    def get_title(self):
        """Returns the title if supplied and user is_external
        SANITY WARNING this function will HIDE the title for internal staff
        """
        return self.title if (self.title and self.is_external) else ""

    def get_middle_initials(self):
        i = self.middle_initials if self.middle_initials else ""
        if len(i)>1:
            return i[1:]
        else:
            return ""

    def guess_first_initial(self):
        return self.first_name[0] if self.first_name else ""

    def get_affiliation(self):
        """Returns the affiliation in parentheses if provided, or an empty string
        """
        a = "({0})".format(self.affiliation) if self.affiliation else ""
        return a

    #--------------------------------------------------------------------------#
    # Required for admin
    @property
    def short_name(self):
        return self.first_name if self.first_name else self.fullname

    def get_short_name(self):
        """Returns the first name as short name for the user
        """
        return self.first_name

    @property
    def full_name(self):
        return self.get_full_name()

    def get_full_name(self):
        """Returns title + first name + initials + last name + affiliation
        """
        if self.is_group:
            full_name = "{0} {1}".format(self.group_name, self.get_affiliation())
        else:
            full_name = "{0} {1} {2} {3} {4}".format(
                self.get_title(),
                self.first_name,
                self.get_middle_initials(),
                self.last_name,
                self.get_affiliation())
        return full_name.strip()
