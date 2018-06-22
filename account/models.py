from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import utilities


class LoginToken(models.Model):
    """
     LoginToken class provides a way for password less login.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    token = models.CharField(max_length=64, default=utilities.generate_security_token)
    expiry_date = models.DateTimeField(default=utilities.days_from_current_time)

    def _srt_(self):
        return "Login token of {}".format(self.user.username)

class Invitation(models.Model):
    """
    This class provides a way to invite users to join the site and being redirected to a selected url.
    """
    email = models.CharField(max_length=256, blank=False)
    name = models.CharField(max_length=256, blank=False)
    url = models.CharField(max_length=256, blank=False)
    token = models.CharField(max_length=64, default=utilities.generate_security_token(10))
    # If this is null then the invitation will be considered as pending.
    # If it's true or false the invitation will be considered as accepted or rejected.
    accepted = models.NullBooleanField()

    def _srt_(self):
        return "Invitation for {}".format(self.email)

# The Profile class extends Django's default user model.
class Profile(models.Model):
    """
    The Profile class is used to associate a profile with a new user.
    """
    TITLE_CHOICES = (
        ('Dr', 'Dr'),
        ('Professor', 'Professor'),
        ('Miss', 'Miss'),
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms')
    )
    # There are packages for this but, meh.
    COUNTRY_CHOICES = (
        ('Romania', 'Romania'),
        ('United States', 'United States'),
        ('Afghanistan', 'Afghanistan'),
        ('Albania', 'Albania'),
        ('Algeria', 'Algeria'),
        ('Andorra', 'Andorra'),
        ('Angola', 'Angola'),
        ('Argentina', 'Argentina'),
        ('Armenia', 'Armenia'),
        ('Australia', 'Australia'),
        ('Austria', 'Austria'),
        ('Azerbaijan', 'Azerbaijan'),
        ('Bahamas', 'Bahamas'),
        ('Bahrain', 'Bahrain'),
        ('Bangladesh', 'Bangladesh'),
        ('Barbados', 'Barbados'),
        ('Belarus', 'Belarus'),
        ('Belgium', 'Belgium'),
        ('Belize', 'Belize'),
        ('Benin', 'Benin'),
        ('Bhutan', 'Bhutan'),
        ('Bolivia', 'Bolivia'),
        ('Bosnia Herzegovina', 'Bosnia Herzegovina'),
        ('Botswana', 'Botswana'),
        ('Brazil', 'Brazil'),
        ('Brunei', 'Brunei'),
        ('Bulgaria', 'Bulgaria'),
        ('Burkina', 'Burkina'),
        ('Burundi', 'Burundi'),
        ('Cambodia', 'Cambodia'),
        ('Cameroon', 'Cameroon'),
        ('Canada', 'Canada'),
        ('Cape Verde', 'Cape Verde'),
        ('Central African Rep', 'Central African Rep'),
        ('Chad', 'Chad'),
        ('Chile', 'Chile'),
        ('China', 'China'),
        ('Colombia', 'Colombia'),
        ('Comoros', 'Comoros'),
        ('Congo', 'Congo'),
        ('Costa Rica', 'Costa Rica'),
        ('Croatia', 'Croatia'),
        ('Cuba', 'Cuba'),
        ('Cyprus', 'Cyprus'),
        ('Czech Republic', 'Czech Republic'),
        ('Denmark', 'Denmark'),
        ('Djibouti', 'Djibouti'),
        ('Dominica', 'Dominica'),
        ('Dominican Republic', 'Dominican Republic'),
        ('East Timor', 'East Timor'),
        ('Ecuador', 'Ecuador'),
        ('Egypt', 'Egypt'),
        ('El Salvador', 'El Salvador'),
        ('Equatorial Guinea', 'Equatorial Guinea'),
        ('Eritrea', 'Eritrea'),
        ('Estonia', 'Estonia'),
        ('Ethiopia', 'Ethiopia'),
        ('Fiji', 'Fiji'),
        ('Finland', 'Finland'),
        ('France', 'France'),
        ('Gabon', 'Gabon'),
        ('Gambia', 'Gambia'),
        ('Georgia', 'Georgia'),
        ('Germany', 'Germany'),
        ('Ghana', 'Ghana'),
        ('Greece', 'Greece'),
        ('Grenada', 'Grenada'),
        ('Guatemala', 'Guatemala'),
        ('Guinea', 'Guinea'),
        ('Guyana', 'Guyana'),
        ('Haiti', 'Haiti'),
        ('Honduras', 'Honduras'),
        ('Hungary', 'Hungary'),
        ('Iceland', 'Iceland'),
        ('India', 'India'),
        ('Indonesia', 'Indonesia'),
        ('Iran', 'Iran'),
        ('Iraq', 'Iraq'),
        ('Ireland', 'Ireland'),
        ('Israel', 'Israel'),
        ('Italy', 'Italy'),
        ('Ivory Coast', 'Ivory Coast'),
        ('Jamaica', 'Jamaica'),
        ('Japan', 'Japan'),
        ('Jordan', 'Jordan'),
        ('Kazakhstan', 'Kazakhstan'),
        ('Kenya', 'Kenya'),
        ('Kiribati', 'Kiribati'),
        ('Korea North', 'Korea North'),
        ('Korea South', 'Korea South'),
        ('Kosovo', 'Kosovo'),
        ('Kuwait', 'Kuwait'),
        ('Kyrgyzstan', 'Kyrgyzstan'),
        ('Laos', 'Laos'),
        ('Latvia', 'Latvia'),
        ('Lebanon', 'Lebanon'),
        ('Lesotho', 'Lesotho'),
        ('Liberia', 'Liberia'),
        ('Libya', 'Libya'),
        ('Liechtenstein', 'Liechtenstein'),
        ('Lithuania', 'Lithuania'),
        ('Luxembourg', 'Luxembourg'),
        ('Macedonia', 'Macedonia'),
        ('Madagascar', 'Madagascar'),
        ('Malawi', 'Malawi'),
        ('Malaysia', 'Malaysia'),
        ('Maldives', 'Maldives'),
        ('Mali', 'Mali'),
        ('Malta', 'Malta'),
        ('Marshall Islands', 'Marshall Islands'),
        ('Mauritania', 'Mauritania'),
        ('Mauritius', 'Mauritius'),
        ('Mexico', 'Mexico'),
        ('Micronesia', 'Micronesia'),
        ('Moldova', 'Moldova'),
        ('Monaco', 'Monaco'),
        ('Mongolia', 'Mongolia'),
        ('Montenegro', 'Montenegro'),
        ('Morocco', 'Morocco'),
        ('Mozambique', 'Mozambique'),
        ('Myanmar', 'Myanmar'),
        ('Namibia', 'Namibia'),
        ('Nauru', 'Nauru'),
        ('Nepal', 'Nepal'),
        ('Netherlands', 'Netherlands'),
        ('New Zealand', 'New Zealand'),
        ('Nicaragua', 'Nicaragua'),
        ('Niger', 'Niger'),
        ('Nigeria', 'Nigeria'),
        ('Norway', 'Norway'),
        ('Oman', 'Oman'),
        ('Pakistan', 'Pakistan'),
        ('Palau', 'Palau'),
        ('Panama', 'Panama'),
        ('Papua New Guinea', 'Papua New Guinea'),
        ('Paraguay', 'Paraguay'),
        ('Peru', 'Peru'),
        ('Philippines', 'Philippines'),
        ('Poland', 'Poland'),
        ('Portugal', 'Portugal'),
        ('Qatar', 'Qatar'),
        ('Russian Federation', 'Russian Federation'),
        ('Rwanda', 'Rwanda'),
        ('St Lucia', 'St Lucia'),
        ('Samoa', 'Samoa'),
        ('San Marino', 'San Marino'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Senegal', 'Senegal'),
        ('Serbia', 'Serbia'),
        ('Seychelles', 'Seychelles'),
        ('Sierra Leone', 'Sierra Leone'),
        ('Singapore', 'Singapore'),
        ('Slovakia', 'Slovakia'),
        ('Slovenia', 'Slovenia'),
        ('Solomon Islands', 'Solomon Islands'),
        ('Somalia', 'Somalia'),
        ('South Africa', 'South Africa'),
        ('South Sudan', 'South Sudan'),
        ('Spain', 'Spain'),
        ('Sri Lanka', 'Sri Lanka'),
        ('Sudan', 'Sudan'),
        ('Suriname', 'Suriname'),
        ('Swaziland', 'Swaziland'),
        ('Sweden', 'Sweden'),
        ('Switzerland', 'Switzerland'),
        ('Syria', 'Syria'),
        ('Taiwan', 'Taiwan'),
        ('Tajikistan', 'Tajikistan'),
        ('Tanzania', 'Tanzania'),
        ('Thailand', 'Thailand'),
        ('Togo', 'Togo'),
        ('Tonga', 'Tonga'),
        ('Tunisia', 'Tunisia'),
        ('Turkey', 'Turkey'),
        ('Turkmenistan', 'Turkmenistan'),
        ('Tuvalu', 'Tuvalu'),
        ('Uganda', 'Uganda'),
        ('Ukraine', 'Ukraine'),
        ('United Arab Emirates', 'United Arab Emirates'),
        ('United Kingdom', 'United Kingdom'),
        ('Uruguay', 'Uruguay'),
        ('Uzbekistan', 'Uzbekistan'),
        ('Vanuatu', 'Vanuatu'),
        ('Vatican City', 'Vatican City'),
        ('Venezuela', 'Venezuela'),
        ('Vietnam', 'Vietnam'),
        ('Yemen', 'Yemen'),
        ('Zambia', 'Zambia'),
        ('Zimbabwe', 'Zimbabwe'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=64, choices=TITLE_CHOICES, default='Dr')
    phone = models.CharField(max_length=64, default='')
    country = models.CharField(max_length=64, choices=COUNTRY_CHOICES, default='Romania')
    affiliation = models.CharField(max_length=64, default='')

    def __srt__(self):
        return "Profile of user: {}".format(self.user.username)


def create_review_invite(email, name, url, lt):
    """
    Creates a pending invitation
    :param email:  The email of the invited user
    :param name:  The name of the invitations
    :param url: The url where to redirect
    :param lt: The Login Token
    :return: Invitation object
    """
    ri = Invitation()
    ri.email = email
    ri.name = name
    ri.url = url
    ri.login_token = lt
    ri.save()

    return ri


def get_login_token(user):
    """
    Returns the LoginToken for the specified user
    :param user: The requested user
    :return: The login token object
    """
    token = LoginToken.objects.filter(user=user)
    return token[0]

def create_login_token(user):
    """
    Creates a new login token and it deletes the older ones
    :param user: The user object on which to assign the login token
    :return: LoginToken object
    """
    # Delete the old token if any.
    token = LoginToken.objects.filter(user=user)
    if token:
        token.delete()

    # Create a new LoginToken
    token = LoginToken()
    token.user = user
    token.save()

    return token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """
        Ensure that every new user gets a profile.
    """
    if created:
        Profile.objects.create(user=instance)