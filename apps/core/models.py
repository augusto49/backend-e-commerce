"""
Core models for the E-commerce Backend.
Contains base models with common fields used across all apps.
Modelos principais para o Backend E-commerce.
Contém modelos base com campos comuns usados em todos os aplicativos.
"""

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    Modelo base abstrato que fornece campos 'created_at'
    e 'updated_at' auto-atualizáveis.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted records by default.
    Manager que filtra registros excluídos logicamente (soft-deleted) por padrão.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """
        Return all records including soft-deleted ones.
        Retorna todos os registros, incluindo os excluídos logicamente.
        """
        return super().get_queryset()

    def deleted_only(self):
        """
        Return only soft-deleted records.
        Retorna apenas registros excluídos logicamente.
        """
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    Modelo base abstrato que fornece funcionalidade de exclusão lógica (soft delete).
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Soft delete the record. Use hard=True to permanently delete.
        Exclui logicamente o registro. Use hard=True para excluir permanentemente.
        """
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)

        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """
        Restore a soft-deleted record.
        Restaura um registro excluído logicamente.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Base model that combines TimeStampedModel and SoftDeleteModel.
    Use this as the base for most models in the application.
    Modelo base que combina TimeStampedModel e SoftDeleteModel.
    Use isso como base para a maioria dos modelos na aplicação.
    """

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model that uses UUID as primary key.
    Modelo base abstrato que usa UUID como chave primária.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
