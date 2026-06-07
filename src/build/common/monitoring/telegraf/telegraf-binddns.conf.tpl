[[inputs.http]]
  urls = [
    "http://{{ ADM_IP }}:8053/json/v1/server"
  ]

  method = "GET"
  name_override = "binddns_statistics"
  data_format = "json"

  tagexclude = [
    "url"
  ]

  [inputs.http.tags]
    role = "{{ ROLE }}"
    node = "{{ NODE_NAME }}"
