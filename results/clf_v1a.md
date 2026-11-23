# v1a Evaluation (email fix only)

Thresholds were selected on `dev_public`; v0 keeps its original threshold. v1a models use a threshold selected to target approximately 2% benign FPR.

| Model | Set | Recall | FPR | F1 |
|---|---|---:|---:|---:|
| v0 | dev_public | 0.9412819363514119 | 0.02017434620174346 | 0.9519492293744334 |
| v0 | external_eval | 0.6091370558375635 | 0.006472491909385114 | 0.7523510971786834 |
| v0 | indirect_eval | 0.6300723497955332 | n/a | 0.77306059436511 |
| v0 | overrefusal_eval | n/a | 0.17155612244897958 | 0.0 |
| v0 | benign_email_probe | n/a | 1.0 | 0.0 |
| v1a_e1 | dev_public | 0.9269385925593904 | 0.02017434620174346 | 0.9442922374429223 |
| v1a_e1 | external_eval | 0.5634517766497462 | 0.006472491909385114 | 0.7161290322580646 |
| v1a_e1 | indirect_eval | 0.6388801509908776 | n/a | 0.7796545105566218 |
| v1a_e1 | overrefusal_eval | n/a | 0.23214285714285715 | 0.0 |
| v1a_e1 | benign_email_probe | n/a | 1.0 | 0.0 |
| v1a_e2 | dev_public | 0.9260421335723891 | 0.02017434620174346 | 0.9438099588853358 |
| v1a_e2 | external_eval | 0.6548223350253807 | 0.006472491909385114 | 0.7865853658536586 |
| v1a_e2 | indirect_eval | 0.6373073293488518 | n/a | 0.7784822286263209 |
| v1a_e2 | overrefusal_eval | n/a | 0.3635204081632653 | 0.0 |
| v1a_e2 | benign_email_probe | n/a | 1.0 | 0.0 |
| rules | dev_public | 0.01927386822052891 | 0.006973848069738481 | 0.03735881841876629 |
| rules | external_eval | 0.01015228426395939 | 0.0 | 0.020100502512562814 |
| rules | indirect_eval | 0.0006291286568103177 | n/a | 0.0012574662055957245 |
| rules | overrefusal_eval | n/a | 0.0 | n/a |
| rules | benign_email_probe | n/a | 0.0 | n/a |
| deberta | dev_public | 0.7458538771851188 | 0.16612702366127025 | 0.7295046032441912 |
| deberta | external_eval | 0.6903553299492385 | 0.016181229773462782 | 0.8047337278106509 |
| deberta | indirect_eval | 0.48663101604278075 | n/a | 0.6546762589928058 |
| deberta | overrefusal_eval | n/a | 0.0548469387755102 | 0.0 |
| deberta | benign_email_probe | n/a | 0.0 | n/a |

## Indirect evaluation scope

LLMail is treated as seen distribution; BIPIA and InjecAgent are treated as unseen. Per-source results are stored in `results/v1a_evaluation.json`.

## Overrefusal

The `overrefusal_eval` source breakdown separates XSTest and OR-Bench in the raw results.

## Shortcut check

The synthetic v1 email rows use different templates and topics from `benign_email_probe`. Exact normalized overlap was checked after regeneration; embedding cosine > 0.9 audit was not rerun in this step.

## Numbers-only comparison

- v1a unseen indirect recall: e1=0.6389, e2=0.6373; v0=0.6301.
- OR-Bench and email-probe FPR remain source-specific in the raw results; email-probe FPR is 1.0000 for v0, v1a_e1, and v1a_e2.

## Limitations

- This is an email-fix-only model family, not the full v1b data fix.
- No model was promoted to the gateway.
