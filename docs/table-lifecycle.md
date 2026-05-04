# Table Lifecycle Notes

## Cleanup Targets

- `password_reset_tokens`: align schema with portal code
- `user_invitations`: separate current-state semantics from historical duplication
- `admin_users`: enforce referential integrity to `auth_users`
- `admin_profiles`: deprecate duplicated identity fields
- `final_profile`: document recompute-only lifecycle
- `conversation_prompt_scores`: define orphan retention/cleanup policy
