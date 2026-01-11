from django.db import transaction


def reaction_action(
    *,
    reaction_model,
    user,
    target_field,
    target,
    reaction_type,
):
    with transaction.atomic():
        old_reaction = reaction_model.objects.filter(
            user=user, **{target_field: target}
        ).first()

        if old_reaction:
            old_type = old_reaction.reaction_type
            old_reaction.delete()

            if old_type == reaction_type:
                return None

        return reaction_model.objects.create(
            user=user,
            **{target_field: target},
            reaction_type=reaction_type,
        )
