from rest_framework.renderers import JSONRenderer

class StandardizedRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code

        # Si c'est une erreur, on laisse le exception handler gérer
        if status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)

        formatted_response = {
            "status_code": status_code,
            "data": data,
            "message": getattr(response, "message", "")
        }

        return super().render(formatted_response, accepted_media_type, renderer_context)