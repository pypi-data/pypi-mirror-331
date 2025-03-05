import logging

import ce_ui.breadcrumb as breadcrumb
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from rest_framework import mixins, viewsets
from topobank.manager.models import Surface
from topobank.usage_stats.utils import increase_statistics_by_date_and_object
from trackstats.models import Metric, Period

from .forms import SurfacePublishForm
from .models import MAX_LEN_AUTHORS_FIELD, Publication
from .serializers import PublicationSerializer
from .utils import NewPublicationTooFastException, PublicationException

_log = logging.getLogger(__name__)


class PublicationViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = PublicationSerializer

    # FIXME! This view needs pagination

    def get_queryset(self):
        q = Publication.objects.all()
        order_by_version = False
        try:
            original_surface = int(
                self.request.query_params.get("original_surface", default=None)
            )
            q = q.filter(original_surface=original_surface)
            order_by_version = True
        except TypeError:
            pass
        try:
            surface = int(self.request.query_params.get("surface", default=None))
            q = q.filter(surface=surface)
            order_by_version = True
        except TypeError:
            pass
        if order_by_version:
            q = q.order_by("-version")
        return q


def go(request, short_url):
    """Visit a published surface by short url."""
    try:
        pub = Publication.objects.get(short_url=short_url)
    except Publication.DoesNotExist:
        raise Http404()

    increase_statistics_by_date_and_object(
        Metric.objects.PUBLICATION_VIEW_COUNT, period=Period.DAY, obj=pub
    )

    if (
        "HTTP_ACCEPT" in request.META
        and "application/json" in request.META["HTTP_ACCEPT"]
    ):
        return redirect(pub.get_api_url())
    else:
        return redirect(
            f"{reverse('ce_ui:surface-detail')}?surface={pub.surface.pk}"
        )  # <- topobank does not know this


class SurfacePublishView(FormView):
    template_name = "surface_publish.html"
    form_class = SurfacePublishForm

    def get_surface(self):
        surface_pk = self.kwargs["pk"]
        return get_object_or_404(Surface, pk=surface_pk)

    def dispatch(self, request, *args, **kwargs):
        surface = self.get_surface()
        if not surface.has_permission(request.user, "full"):
            raise PermissionDenied(
                f"User {request.user} does not have permission to "
                "publish this dataset."
            )
        return super().dispatch(request, *args, *kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["author_0"] = ""
        initial["num_author_fields"] = 1
        return initial

    def get_success_url(self):
        return f"{reverse('ce_ui:surface-detail')}?surface={self.kwargs['pk']}"

    def form_valid(self, form):
        license = form.cleaned_data.get("license")
        authors = form.cleaned_data.get("authors_json")
        surface = self.get_surface()
        try:
            Publication.publish(surface, license, self.request.user, authors)
        except NewPublicationTooFastException:
            return redirect(
                "publication:surface-publication-rate-too-high", pk=surface.pk
            )
        except PublicationException as exc:
            msg = f"Publication failed, reason: {exc}"
            _log.error(msg)
            messages.error(self.request, msg)
            return redirect("publication:surface-publication-error", pk=surface.pk)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        surface = self.get_surface()

        breadcrumb.add_surface(context, surface)
        breadcrumb.prepare_context(context)
        context["extra_tabs"] += [
            {
                "title": "Publish surface?",
                "icon": "bullhorn",
                "href": self.request.path,
                "active": True,
                "tooltip": f"Publishing surface '{surface.label}'",
            }
        ]
        context["surface"] = surface
        context["max_len_authors_field"] = MAX_LEN_AUTHORS_FIELD
        user = self.request.user
        context["user_dict"] = dict(
            first_name=user.first_name, last_name=user.last_name, orcid_id=user.orcid_id
        )
        context["configured_for_doi_generation"] = settings.PUBLICATION_DOI_MANDATORY
        return context


class PublicationRateTooHighView(TemplateView):
    template_name = "publication_rate_too_high.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["min_seconds"] = settings.MIN_SECONDS_BETWEEN_SAME_SURFACE_PUBLICATIONS

        surface_pk = self.kwargs["pk"]
        surface = get_object_or_404(Surface, pk=surface_pk)

        breadcrumb.add_surface(context, surface)
        breadcrumb.prepare_context(context)
        context["extra_tabs"] += [
            {
                "title": "Publication rate too high",
                "icon": "bolt",
                "href": self.request.path,
                "active": True,
            }
        ]
        return context


class PublicationErrorView(TemplateView):
    template_name = "publication_error.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        surface_pk = self.kwargs["pk"]
        surface = get_object_or_404(Surface, pk=surface_pk)

        breadcrumb.add_surface(context, surface)
        breadcrumb.prepare_context(context)
        context["extra_tabs"] += [
            {
                "title": "Publication error",
                "icon": "bolt",
                "href": self.request.path,
                "active": True,
            }
        ]
        return context
