import uuid

from slugify import slugify


class SlugGeneratorMixin:
    slug_field_name = None
    SAVE_LIMIT = 100

    def save(self, *args, **kwargs):
        if not self.slug_field_name:
            raise AttributeError(
                f"{self.__class__.__name__}: slug_field_name is not set"
            )

        if not hasattr(self, self.slug_field_name):
            raise AttributeError(
                f"{self.__class__.__name__}: field with {self.slug_field_name} is not set"
            )

        if not self.slug:
            slug_value = None

            value = getattr(self, self.slug_field_name)
            if value:
                slug_value = str(value)

            if not slug_value:
                raise AttributeError("No valid field found for slug generation")

            base_slug = generate_slug(slug_value)

            model_class = self.__class__
            candidate = base_slug
            counter = 1

            while model_class.objects.filter(slug=candidate).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
                if counter > self.SAVE_LIMIT:
                    candidate = f"{base_slug}-{uuid.uuid4().hex[:8]}"
                    break

            self.slug = candidate

        return super().save(*args, **kwargs)


def generate_slug(value):
    base_slug = slugify(value)
    if not base_slug:
        base_slug = "item"

    return base_slug
