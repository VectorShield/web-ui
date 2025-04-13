{{- define "web-ui.name" -}}
{{- .Chart.Name | default "web-ui" -}}
{{- end -}}

{{- define "web-ui.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | replace "." "_" -}}
{{- end -}}

{{- define "web-ui.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else if .Values.nameOverride }}
{{- .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "web-ui.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end }}
{{- end -}}
