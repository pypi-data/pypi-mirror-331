from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CRUDEvent(models.Model):
    CREATE = 1
    UPDATE = 2
    DELETE = 3
    M2M_CHANGE = 4
    M2M_CHANGE_REV = 5
    M2M_ADD = 6
    M2M_ADD_REV = 7
    M2M_REMOVE = 8
    M2M_REMOVE_REV = 9
    M2M_CLEAR = 10
    M2M_CLEAR_REV = 11

    TYPES = (
        (CREATE, _("Create")),
        (UPDATE, _("Update")),
        (DELETE, _("Delete")),
        (M2M_CHANGE, _("Many-to-Many Change")),
        (M2M_CHANGE_REV, _("Reverse Many-to-Many Change")),
        (M2M_ADD, _("Many-to-Many Add")),
        (M2M_ADD_REV, _("Reverse Many-to-Many Add")),
        (M2M_REMOVE, _("Many-to-Many Remove")),
        (M2M_REMOVE_REV, _("Reverse Many-to-Many Remove")),
        (M2M_CLEAR, _("Many-to-Many Clear")),
        (M2M_CLEAR_REV, _("Reverse Many-to-Many Clear")),
    )

    event_type = models.SmallIntegerField(choices=TYPES, verbose_name=_("Event type"))
    object_id = models.CharField(max_length=255, verbose_name=_("Object ID"))
    object_repr = models.TextField(
        default="", blank=True, verbose_name=_("Object representation")
    )
    object_json_repr = models.TextField(
        default="", blank=True, verbose_name=_("Object JSON representation")
    )
    changed_fields = models.TextField(
        default="", blank=True, verbose_name=_("Changed fields")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_constraint=False,
        verbose_name=_("User"),
    )
    user_pk_as_string = models.CharField(
        max_length=255,
        default="",
        blank=True,
        help_text=_("String version of the user pk"),
        verbose_name=_("User PK as string"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date time"))

    class Meta:
        verbose_name = _("CRUD event")
        verbose_name_plural = _("CRUD events")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["object_id"])]

    def is_create(self):
        return self.event_type == self.CREATE

    def is_update(self):
        return self.event_type == self.UPDATE

    def is_delete(self):
        return self.event_type == self.DELETE


class LoginEvent(models.Model):
    LOGIN = 0
    LOGOUT = 1
    FAILED = 2
    TYPES = (
        (LOGIN, _("Login")),
        (LOGOUT, _("Logout")),
        (FAILED, _("Failed login")),
    )
    login_type = models.SmallIntegerField(choices=TYPES, verbose_name=_("Event type"))
    username = models.CharField(
        max_length=255, default="", blank=True, verbose_name=_("Username")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_constraint=False,
        verbose_name=_("User"),
    )
    remote_ip = models.CharField(
        max_length=50, default="", db_index=True, verbose_name=_("Remote IP")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date time"))

    class Meta:
        verbose_name = _("login event")
        verbose_name_plural = _("login events")
        ordering = ["-created_at"]
