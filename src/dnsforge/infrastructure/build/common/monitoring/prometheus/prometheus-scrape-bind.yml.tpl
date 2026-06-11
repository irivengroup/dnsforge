scrape_configs:

  - job_name: "binddns"
    metrics_path: /metrics
    static_configs:
      - targets:
          - "{{ ADM_IP }}:9119"
        labels:
          role: "{{ ROLE }}"
          node: "{{ NODE_NAME }}"
