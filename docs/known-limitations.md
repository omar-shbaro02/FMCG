# Known limitations

- Classification thresholds and owners are version-one FMCG defaults requiring
  controlled-pilot calibration, never silent mutation.
- The UI uses one client shell rather than distinct URLs for each workflow view.
- PDF is a text-first, single-page MVP artifact.
- Redis worker execution is not configured; current pipeline is synchronous.
- Rate limiting is per API process, not distributed.
- Malware scanning, SSO, tenant isolation, and managed secrets are deployment
  integrations.
- TimesFM weights are not bundled and the mock adapter is not production proof.
