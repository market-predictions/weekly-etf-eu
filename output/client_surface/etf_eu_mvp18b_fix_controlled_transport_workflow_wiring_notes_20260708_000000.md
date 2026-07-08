# ETF-EU-MVP18B-FIX workflow wiring notes

```text
work_package_id=ETF-EU-MVP18B-FIX
source_work_package=ETF-EU-MVP18B
fix_type=controlled_transport_workflow_wiring
primary_bootstrap_workflow_changed=false
standalone_controlled_transport_workflow_created=true
controlled_transport_workflow_path=.github/workflows/send-weekly-etf-eu-controlled-transport.yml
sender_entrypoint_path=runtime/send_etf_eu_controlled_report.py
evidence_writer_path=runtime/write_etf_eu_delivery_evidence.py
real_transport_performed=false
receipt_confirmed=false
completion_claimed=false
selected_next_package=ETF-EU-MVP18C
```

MVP18B-FIX wires controlled transport through a separate manual workflow because replacing the large bootstrap workflow was blocked by connector filtering. The next package is a single controlled transport run using the new workflow.
