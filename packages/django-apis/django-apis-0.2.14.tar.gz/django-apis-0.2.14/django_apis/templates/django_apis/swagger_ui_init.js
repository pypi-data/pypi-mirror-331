window.onload = function () {
    var server = window.location.protocol + "//" + window.location.host;
    window.ui = SwaggerUIBundle({
      urls: [{% for site in sites %}{
        url: server + "{% url "django_apis_swagger_ui_data" %}?site={{site}}",
        name: "{{site}}"
      }{% if not forloop.last%},{% endif %}{% endfor %}],
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIStandalonePreset
      ],
      plugins: [
        SwaggerUIBundle.plugins.DownloadUrl
      ],
      layout: "StandaloneLayout"
    });
  
  };
  