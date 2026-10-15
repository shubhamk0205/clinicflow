{{- define "clinicflow.name" -}}{{ .Release.Name }}{{- end }}

{{- define "clinicflow.labels" -}}
app.kubernetes.io/part-of: clinicflow
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{- define "clinicflow.imagePullSecrets" -}}
{{- with .Values.imagePullSecrets }}
imagePullSecrets:
{{ toYaml . | indent 2 }}
{{- end }}
{{- end }}
