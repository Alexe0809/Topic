from django.db import transaction
from django.db.models import Count, Q


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


def get_dict_with_reaction_counts(reaction_model, target_field, target):
    """
    return dict with fields {like,dislike}
    don't use for [topics], only for 1 topic action
    """
    reactions = reaction_model.objects.filter(
        **{target_field: target}
    ).aggregate(
        likes=Count(
            "id", filter=Q(reaction_type=reaction_model.ReactionType.LIKE)
        ),
        dislikes=Count(
            "id", filter=Q(reaction_type=reaction_model.ReactionType.DISLIKE)
        ),
    )
    return reactions
