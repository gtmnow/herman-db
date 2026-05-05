# Table Lifecycle Notes

## Cleanup Targets

- `password_reset_tokens`: aligned with portal code on `user_id_hash`
- `user_invitations`: current-state semantics normalized via `is_current`
- `admin_users`: referential integrity enforced to `auth_users`
- `admin_profiles`: retired by `20260505_0013`; identity now lives in `auth_users`
- `final_profile`: recompute-only lifecycle normalized in `20260505_0011`
- `conversation_prompt_scores`: orphan retention policy normalized with explicit deletion markers
- `user_membership_profiles`: narrowed to membership-specific metadata only in `20260505_0014`
- `reseller_tenant_defaults`: platform-managed defaults normalized to stop storing duplicated provider/model/endpoint fields in `20260505_0014`
