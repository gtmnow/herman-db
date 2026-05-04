-- Live shared Herman schema snapshot generated from PostgreSQL reflection on 2026-05-04
-- Note: this is a baseline contract snapshot, not a migration source of truth.


CREATE TABLE admin_users (
	id VARCHAR(36) NOT NULL, 
	user_id_hash VARCHAR(200) NOT NULL, 
	role VARCHAR(50) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT admin_users_pkey PRIMARY KEY (id)
);


CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);


CREATE TABLE alembic_version_herman_portal (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_herman_portal_pkc PRIMARY KEY (version_num)
);


CREATE TABLE auth_mfa_challenges (
	id SERIAL NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	challenge_type VARCHAR(64) DEFAULT 'email_code'::character varying NOT NULL, 
	requested_app VARCHAR(64) DEFAULT 'herman_admin'::character varying NOT NULL, 
	code_hash VARCHAR(255) NOT NULL, 
	expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	consumed_at TIMESTAMP WITHOUT TIME ZONE, 
	attempt_count INTEGER DEFAULT 0 NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT auth_mfa_challenges_pkey PRIMARY KEY (id)
);


CREATE TABLE auth_sessions (
	session_token_hash VARCHAR(255) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	revoked_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	last_seen_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	admin_mfa_verified_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT auth_sessions_pkey PRIMARY KEY (session_token_hash)
);


CREATE TABLE auth_users (
	id SERIAL NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	display_name VARCHAR(255), 
	tenant_id VARCHAR(255) DEFAULT 'tenant_demo'::character varying NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	is_admin BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	last_login_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT auth_users_pkey PRIMARY KEY (id), 
	CONSTRAINT auth_users_user_id_hash_key UNIQUE NULLS DISTINCT (user_id_hash)
);


CREATE TABLE behaviorial_adj (
	user_id_hash VARCHAR(255) NOT NULL, 
	structure DOUBLE PRECISION NOT NULL, 
	answer_first DOUBLE PRECISION NOT NULL, 
	tone_directness DOUBLE PRECISION NOT NULL, 
	detail_level DOUBLE PRECISION NOT NULL, 
	ambiguity_reduction DOUBLE PRECISION NOT NULL, 
	exploration_level DOUBLE PRECISION NOT NULL, 
	context_loading DOUBLE PRECISION NOT NULL, 
	profile_version VARCHAR(50) NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	prompt_enforcement_level VARCHAR(20) DEFAULT 'none'::character varying NOT NULL, 
	compliance_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	pii_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	CONSTRAINT behaviorial_adj_pkey PRIMARY KEY (user_id_hash)
);


CREATE TABLE brain_chemistry (
	user_id_hash VARCHAR(255) NOT NULL, 
	structure DOUBLE PRECISION NOT NULL, 
	answer_first DOUBLE PRECISION NOT NULL, 
	tone_directness DOUBLE PRECISION NOT NULL, 
	detail_level DOUBLE PRECISION NOT NULL, 
	ambiguity_reduction DOUBLE PRECISION NOT NULL, 
	exploration_level DOUBLE PRECISION NOT NULL, 
	context_loading DOUBLE PRECISION NOT NULL, 
	profile_version VARCHAR(50) NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	prompt_enforcement_level VARCHAR(20) DEFAULT 'none'::character varying NOT NULL, 
	compliance_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	pii_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	CONSTRAINT brain_chemistry_pkey PRIMARY KEY (user_id_hash)
);


CREATE TABLE conversation_folders (
	id VARCHAR(36) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT conversation_folders_pkey PRIMARY KEY (id)
);


CREATE TABLE conversation_prompt_scores (
	id SERIAL NOT NULL, 
	conversation_id VARCHAR(255) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	task_type VARCHAR(100) DEFAULT 'unknown'::character varying NOT NULL, 
	conversation_started_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	conversation_ended_at TIMESTAMP WITH TIME ZONE, 
	last_scored_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	conversation_deleted_at TIMESTAMP WITH TIME ZONE, 
	enforcement_level VARCHAR(20) DEFAULT 'none'::character varying NOT NULL, 
	initial_score INTEGER NOT NULL, 
	best_score INTEGER NOT NULL, 
	final_score INTEGER NOT NULL, 
	improvement_score INTEGER DEFAULT 0 NOT NULL, 
	best_improvement_score INTEGER DEFAULT 0 NOT NULL, 
	policy_completion_score INTEGER, 
	policy_passed BOOLEAN DEFAULT false NOT NULL, 
	passed_without_coaching BOOLEAN DEFAULT false NOT NULL, 
	reached_policy_complete BOOLEAN DEFAULT false NOT NULL, 
	coaching_turn_count INTEGER DEFAULT 0 NOT NULL, 
	blocked_turn_count INTEGER DEFAULT 0 NOT NULL, 
	transformed_turn_count INTEGER DEFAULT 0 NOT NULL, 
	who_status VARCHAR(20) DEFAULT 'missing'::character varying NOT NULL, 
	task_status VARCHAR(20) DEFAULT 'missing'::character varying NOT NULL, 
	context_status VARCHAR(20) DEFAULT 'missing'::character varying NOT NULL, 
	output_status VARCHAR(20) DEFAULT 'missing'::character varying NOT NULL, 
	score_details_json JSON DEFAULT '{}'::json NOT NULL, 
	scoring_version VARCHAR(50) DEFAULT 'v1'::character varying NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	initial_llm_score INTEGER, 
	best_llm_score INTEGER, 
	final_llm_score INTEGER, 
	CONSTRAINT conversation_prompt_scores_pkey PRIMARY KEY (id), 
	CONSTRAINT conversation_prompt_scores_conversation_id_key UNIQUE NULLS DISTINCT (conversation_id)
);


CREATE TABLE conversations (
	id VARCHAR(255) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	transformer_conversation JSON, 
	folder_id VARCHAR(36), 
	CONSTRAINT conversations_pkey PRIMARY KEY (id)
);


CREATE TABLE database_instance_configs (
	id VARCHAR(36) NOT NULL, 
	label VARCHAR(200) NOT NULL, 
	db_kind VARCHAR(50) NOT NULL, 
	host VARCHAR(200), 
	database_name VARCHAR(200), 
	connection_string_masked VARCHAR(500), 
	notes TEXT, 
	is_active BOOLEAN NOT NULL, 
	managed_via_db_only BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	connection_secret_reference VARCHAR(255), 
	secret_source VARCHAR(30) DEFAULT 'none'::character varying, 
	vault_provider VARCHAR(50), 
	CONSTRAINT database_instance_configs_pkey PRIMARY KEY (id)
);


CREATE TABLE environment_details (
	user_id_hash VARCHAR(255) NOT NULL, 
	structure DOUBLE PRECISION NOT NULL, 
	answer_first DOUBLE PRECISION NOT NULL, 
	tone_directness DOUBLE PRECISION NOT NULL, 
	detail_level DOUBLE PRECISION NOT NULL, 
	ambiguity_reduction DOUBLE PRECISION NOT NULL, 
	exploration_level DOUBLE PRECISION NOT NULL, 
	context_loading DOUBLE PRECISION NOT NULL, 
	profile_version VARCHAR(50) NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	prompt_enforcement_level VARCHAR(20) DEFAULT 'none'::character varying NOT NULL, 
	compliance_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	pii_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	CONSTRAINT environment_details_pkey PRIMARY KEY (user_id_hash)
);


CREATE TABLE feedback (
	id VARCHAR(36) NOT NULL, 
	turn_id VARCHAR(255) NOT NULL, 
	conversation_id VARCHAR(255) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	feedback_type VARCHAR(16) NOT NULL, 
	selected_dimensions JSON NOT NULL, 
	comments TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT feedback_pkey PRIMARY KEY (id)
);


CREATE TABLE final_profile (
	user_id_hash VARCHAR(255) NOT NULL, 
	structure DOUBLE PRECISION NOT NULL, 
	answer_first DOUBLE PRECISION NOT NULL, 
	tone_directness DOUBLE PRECISION NOT NULL, 
	detail_level DOUBLE PRECISION NOT NULL, 
	ambiguity_reduction DOUBLE PRECISION NOT NULL, 
	exploration_level DOUBLE PRECISION NOT NULL, 
	context_loading DOUBLE PRECISION NOT NULL, 
	profile_version VARCHAR(50) NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	prompt_enforcement_level VARCHAR(20) DEFAULT 'none'::character varying NOT NULL, 
	compliance_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	pii_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	CONSTRAINT final_profile_pkey PRIMARY KEY (user_id_hash)
);


CREATE TABLE platform_managed_llm_configs (
	id VARCHAR(36) NOT NULL, 
	label VARCHAR(200) NOT NULL, 
	provider_type VARCHAR(100) NOT NULL, 
	model_name VARCHAR(200) NOT NULL, 
	endpoint_url VARCHAR(500), 
	api_key_masked VARCHAR(32), 
	secret_reference VARCHAR(255), 
	secret_source VARCHAR(30) NOT NULL, 
	vault_provider VARCHAR(50), 
	notes TEXT, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT platform_managed_llm_configs_pkey PRIMARY KEY (id)
);


CREATE TABLE prompt_transform_requests (
	id SERIAL NOT NULL, 
	session_id VARCHAR(255) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	raw_prompt TEXT NOT NULL, 
	transformed_prompt TEXT, 
	task_type VARCHAR(100) NOT NULL, 
	target_provider VARCHAR(100) NOT NULL, 
	target_model VARCHAR(100) NOT NULL, 
	persona_source VARCHAR(100) NOT NULL, 
	used_fallback_model BOOLEAN DEFAULT false NOT NULL, 
	metadata_json JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	conversation_id VARCHAR(255) DEFAULT ''::character varying NOT NULL, 
	result_type VARCHAR(50) DEFAULT 'transformed'::character varying NOT NULL, 
	coaching_tip TEXT, 
	blocking_message TEXT, 
	enforcement_level VARCHAR(20) DEFAULT 'none'::character varying NOT NULL, 
	compliance_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	pii_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	conversation_json JSON DEFAULT '{}'::json NOT NULL, 
	findings_json JSON DEFAULT '[]'::json NOT NULL, 
	token_usage_json JSON, 
	CONSTRAINT prompt_transform_requests_pkey PRIMARY KEY (id)
);


CREATE TABLE prompt_ui_instance_configs (
	id VARCHAR(36) NOT NULL, 
	label VARCHAR(200) NOT NULL, 
	base_url VARCHAR(500) NOT NULL, 
	notes TEXT, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT prompt_ui_instance_configs_pkey PRIMARY KEY (id)
);


CREATE TABLE reseller_partners (
	id VARCHAR(36) NOT NULL, 
	reseller_key VARCHAR(100) NOT NULL, 
	reseller_name VARCHAR(200) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	service_tier_definition_id VARCHAR(36), 
	lifecycle_snapshot_json TEXT, 
	CONSTRAINT reseller_partners_pkey PRIMARY KEY (id)
);


CREATE TABLE service_tier_definitions (
	id VARCHAR(36) NOT NULL, 
	scope_type VARCHAR(30) NOT NULL, 
	tier_key VARCHAR(100) NOT NULL, 
	tier_name VARCHAR(200) NOT NULL, 
	description TEXT, 
	max_users INTEGER, 
	has_unlimited_users BOOLEAN NOT NULL, 
	max_organizations INTEGER, 
	monthly_admin_fee DOUBLE PRECISION, 
	per_active_user_fee DOUBLE PRECISION, 
	additional_usage_fee TEXT, 
	cqi_assessment INTEGER, 
	billing_notes TEXT, 
	is_active BOOLEAN NOT NULL, 
	sort_order INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT service_tier_definitions_pkey PRIMARY KEY (id), 
	CONSTRAINT service_tier_definitions_scope_type_tier_key_key UNIQUE NULLS DISTINCT (scope_type, tier_key)
);


CREATE TABLE type_detail (
	user_id_hash VARCHAR(255) NOT NULL, 
	structure DOUBLE PRECISION NOT NULL, 
	answer_first DOUBLE PRECISION NOT NULL, 
	tone_directness DOUBLE PRECISION NOT NULL, 
	detail_level DOUBLE PRECISION NOT NULL, 
	ambiguity_reduction DOUBLE PRECISION NOT NULL, 
	exploration_level DOUBLE PRECISION NOT NULL, 
	context_loading DOUBLE PRECISION NOT NULL, 
	profile_version VARCHAR(50) NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	prompt_enforcement_level VARCHAR(20) DEFAULT 'none'::character varying NOT NULL, 
	compliance_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	pii_check_enabled BOOLEAN DEFAULT false NOT NULL, 
	CONSTRAINT type_detail_pkey PRIMARY KEY (user_id_hash)
);


CREATE TABLE vault_secrets (
	id VARCHAR(36) NOT NULL, 
	secret_ref VARCHAR(255) NOT NULL, 
	provider_type VARCHAR(50) NOT NULL, 
	scope_type VARCHAR(50) NOT NULL, 
	scope_id VARCHAR(200) NOT NULL, 
	secret_kind VARCHAR(50) NOT NULL, 
	display_name VARCHAR(200), 
	secret_masked VARCHAR(64), 
	ciphertext TEXT NOT NULL, 
	metadata_json TEXT DEFAULT '{}'::text NOT NULL, 
	created_by_admin_user_id VARCHAR(36), 
	last_accessed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT vault_secrets_pkey PRIMARY KEY (id), 
	CONSTRAINT vault_secrets_secret_ref_key UNIQUE NULLS DISTINCT (secret_ref)
);


CREATE TABLE admin_audit_log (
	id VARCHAR(36) NOT NULL, 
	actor_admin_user_id VARCHAR(36) NOT NULL, 
	action_type VARCHAR(100) NOT NULL, 
	target_type VARCHAR(100) NOT NULL, 
	target_id VARCHAR(200) NOT NULL, 
	before_json TEXT, 
	after_json TEXT, 
	request_id VARCHAR(100), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT admin_audit_log_pkey PRIMARY KEY (id), 
	CONSTRAINT admin_audit_log_actor_admin_user_id_fkey FOREIGN KEY(actor_admin_user_id) REFERENCES admin_users (id)
);


CREATE TABLE admin_permissions (
	id VARCHAR(36) NOT NULL, 
	admin_user_id VARCHAR(36) NOT NULL, 
	permission_key VARCHAR(100) NOT NULL, 
	CONSTRAINT admin_permissions_pkey PRIMARY KEY (id), 
	CONSTRAINT admin_permissions_admin_user_id_fkey FOREIGN KEY(admin_user_id) REFERENCES admin_users (id), 
	CONSTRAINT admin_permissions_admin_user_id_permission_key_key UNIQUE NULLS DISTINCT (admin_user_id, permission_key)
);


CREATE TABLE admin_profiles (
	id VARCHAR(36) NOT NULL, 
	admin_user_id VARCHAR(36) NOT NULL, 
	display_name VARCHAR(200), 
	email VARCHAR(200), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT admin_profiles_pkey PRIMARY KEY (id), 
	CONSTRAINT admin_profiles_admin_user_id_fkey FOREIGN KEY(admin_user_id) REFERENCES admin_users (id)
);


CREATE TABLE admin_sessions (
	id VARCHAR(64) NOT NULL, 
	admin_user_id VARCHAR(36) NOT NULL, 
	user_id_hash VARCHAR(200) NOT NULL, 
	issued_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	mfa_verified_at TIMESTAMP WITH TIME ZONE, 
	user_agent VARCHAR(1000), 
	source_ip VARCHAR(100), 
	CONSTRAINT admin_sessions_pkey PRIMARY KEY (id), 
	CONSTRAINT admin_sessions_admin_user_id_fkey FOREIGN KEY(admin_user_id) REFERENCES admin_users (id)
);


CREATE TABLE auth_user_credentials (
	user_id_hash VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	password_algorithm VARCHAR(64) DEFAULT 'bcrypt'::character varying NOT NULL, 
	password_set_at TIMESTAMP WITHOUT TIME ZONE, 
	failed_login_attempts INTEGER DEFAULT 0 NOT NULL, 
	locked_until TIMESTAMP WITHOUT TIME ZONE, 
	last_login_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT auth_user_credentials_pkey PRIMARY KEY (user_id_hash), 
	CONSTRAINT fk_auth_user_credentials_user FOREIGN KEY(user_id_hash) REFERENCES auth_users (user_id_hash)
);


CREATE TABLE conversation_turns (
	id VARCHAR(36) NOT NULL, 
	conversation_id VARCHAR(255) NOT NULL, 
	user_text TEXT NOT NULL, 
	transformed_text TEXT NOT NULL, 
	assistant_text TEXT NOT NULL, 
	assistant_images JSON NOT NULL, 
	transformation_applied BOOLEAN NOT NULL, 
	summary_type INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	coaching_text TEXT DEFAULT ''::text, 
	coaching_requirements JSON, 
	assistant_kind VARCHAR(20) DEFAULT 'assistant'::character varying, 
	CONSTRAINT conversation_turns_pkey PRIMARY KEY (id), 
	CONSTRAINT conversation_turns_conversation_id_fkey FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);


CREATE TABLE guide_me_sessions (
	id VARCHAR(36) NOT NULL, 
	conversation_id VARCHAR(255) NOT NULL, 
	user_id_hash VARCHAR(255) NOT NULL, 
	status VARCHAR(24) NOT NULL, 
	current_step VARCHAR(24) NOT NULL, 
	answers JSON NOT NULL, 
	personalization JSON NOT NULL, 
	guidance_text TEXT NOT NULL, 
	follow_up_questions JSON NOT NULL, 
	final_prompt TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	CONSTRAINT guide_me_sessions_pkey PRIMARY KEY (id), 
	CONSTRAINT guide_me_sessions_conversation_id_fkey FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);


CREATE TABLE password_reset_tokens (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	token_hash VARCHAR(255) NOT NULL, 
	expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	used_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id), 
	CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY(user_id) REFERENCES auth_users (id) ON DELETE CASCADE
);


CREATE TABLE report_export_jobs (
	id VARCHAR(36) NOT NULL, 
	requested_by_admin_user_id VARCHAR(36) NOT NULL, 
	report_type VARCHAR(100) NOT NULL, 
	scope_type VARCHAR(30) NOT NULL, 
	scope_id VARCHAR(200) NOT NULL, 
	filters_json TEXT NOT NULL, 
	format VARCHAR(10) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	file_path VARCHAR(500), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	CONSTRAINT report_export_jobs_pkey PRIMARY KEY (id), 
	CONSTRAINT report_export_jobs_requested_by_admin_user_id_fkey FOREIGN KEY(requested_by_admin_user_id) REFERENCES admin_users (id)
);


CREATE TABLE reseller_tenant_defaults (
	id VARCHAR(36) NOT NULL, 
	reseller_partner_id VARCHAR(36) NOT NULL, 
	default_plan_tier VARCHAR(100), 
	default_reporting_timezone VARCHAR(80), 
	default_service_mode VARCHAR(50), 
	default_portal_base_url VARCHAR(500), 
	default_portal_logo_url VARCHAR(500), 
	default_portal_welcome_message TEXT, 
	default_enforcement_mode VARCHAR(30), 
	default_reporting_enabled BOOLEAN NOT NULL, 
	default_export_enabled BOOLEAN NOT NULL, 
	default_raw_prompt_retention_enabled BOOLEAN NOT NULL, 
	default_raw_prompt_admin_visibility BOOLEAN NOT NULL, 
	default_data_retention_days INTEGER, 
	default_feature_flags_json TEXT NOT NULL, 
	default_credential_mode VARCHAR(30) NOT NULL, 
	default_platform_managed_config_id VARCHAR(36), 
	default_provider_type VARCHAR(100), 
	default_model_name VARCHAR(200), 
	default_endpoint_url VARCHAR(500), 
	default_transformation_enabled BOOLEAN NOT NULL, 
	default_scoring_enabled BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	default_service_tier_definition_id VARCHAR(36), 
	CONSTRAINT reseller_tenant_defaults_pkey PRIMARY KEY (id), 
	CONSTRAINT reseller_tenant_defaults_reseller_partner_id_fkey FOREIGN KEY(reseller_partner_id) REFERENCES reseller_partners (id)
);


CREATE TABLE tenants (
	id VARCHAR(36) NOT NULL, 
	tenant_key VARCHAR(100) NOT NULL, 
	tenant_name VARCHAR(200) NOT NULL, 
	reseller_partner_id VARCHAR(36), 
	status VARCHAR(30) NOT NULL, 
	plan_tier VARCHAR(100), 
	reporting_timezone VARCHAR(80) NOT NULL, 
	external_customer_id VARCHAR(200), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	service_tier_definition_id VARCHAR(36), 
	CONSTRAINT tenants_pkey PRIMARY KEY (id), 
	CONSTRAINT tenants_reseller_partner_id_fkey FOREIGN KEY(reseller_partner_id) REFERENCES reseller_partners (id)
);


CREATE TABLE groups (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	group_name VARCHAR(200) NOT NULL, 
	group_type VARCHAR(100), 
	parent_group_id VARCHAR(36), 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT groups_pkey PRIMARY KEY (id), 
	CONSTRAINT groups_parent_group_id_fkey FOREIGN KEY(parent_group_id) REFERENCES groups (id), 
	CONSTRAINT groups_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE tenant_llm_config (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	provider_type VARCHAR(100) NOT NULL, 
	model_name VARCHAR(200) NOT NULL, 
	endpoint_url VARCHAR(500), 
	api_key_masked VARCHAR(32), 
	secret_reference VARCHAR(255), 
	credential_mode VARCHAR(30) NOT NULL, 
	credential_status VARCHAR(30) NOT NULL, 
	last_validated_at TIMESTAMP WITH TIME ZONE, 
	last_validation_message TEXT, 
	transformation_enabled BOOLEAN NOT NULL, 
	scoring_enabled BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	secret_source VARCHAR(30) DEFAULT 'none'::character varying, 
	vault_provider VARCHAR(50), 
	platform_managed_config_id VARCHAR(36), 
	CONSTRAINT tenant_llm_config_pkey PRIMARY KEY (id), 
	CONSTRAINT tenant_llm_config_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE tenant_onboarding_status (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	tenant_created BOOLEAN NOT NULL, 
	llm_configured BOOLEAN NOT NULL, 
	llm_validated BOOLEAN NOT NULL, 
	groups_created BOOLEAN NOT NULL, 
	users_uploaded BOOLEAN NOT NULL, 
	admin_assigned BOOLEAN NOT NULL, 
	first_login_detected BOOLEAN NOT NULL, 
	first_transform_detected BOOLEAN NOT NULL, 
	first_score_detected BOOLEAN NOT NULL, 
	onboarding_status VARCHAR(30) NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT tenant_onboarding_status_pkey PRIMARY KEY (id), 
	CONSTRAINT tenant_onboarding_status_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE tenant_portal_configs (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	portal_base_url VARCHAR(500) NOT NULL, 
	logo_url VARCHAR(1000), 
	welcome_message TEXT, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_by_admin_user_id VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	CONSTRAINT tenant_portal_configs_pkey PRIMARY KEY (id), 
	CONSTRAINT tenant_portal_configs_created_by_admin_user_id_fkey FOREIGN KEY(created_by_admin_user_id) REFERENCES admin_users (id), 
	CONSTRAINT tenant_portal_configs_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE tenant_profiles (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	organization_type VARCHAR(100), 
	industry VARCHAR(100), 
	primary_contact_name VARCHAR(200), 
	primary_contact_email VARCHAR(200), 
	service_mode VARCHAR(50), 
	deployment_notes TEXT, 
	last_activity_at TIMESTAMP WITH TIME ZONE, 
	utilization_pct INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT tenant_profiles_pkey PRIMARY KEY (id), 
	CONSTRAINT tenant_profiles_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE tenant_runtime_settings (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	enforcement_mode VARCHAR(30) NOT NULL, 
	reporting_enabled BOOLEAN NOT NULL, 
	export_enabled BOOLEAN NOT NULL, 
	raw_prompt_retention_enabled BOOLEAN NOT NULL, 
	raw_prompt_admin_visibility BOOLEAN NOT NULL, 
	data_retention_days INTEGER, 
	feature_flags_json TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT tenant_runtime_settings_pkey PRIMARY KEY (id), 
	CONSTRAINT tenant_runtime_settings_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE user_invitations (
	id VARCHAR(36) NOT NULL, 
	user_id_hash VARCHAR(200) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	email VARCHAR(200) NOT NULL, 
	invite_token_hash VARCHAR(128) NOT NULL, 
	invite_url VARCHAR(1000), 
	status VARCHAR(30) DEFAULT 'pending'::character varying NOT NULL, 
	provider VARCHAR(50), 
	provider_message_id VARCHAR(255), 
	sent_at TIMESTAMP WITH TIME ZONE, 
	accepted_at TIMESTAMP WITH TIME ZONE, 
	last_error TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	created_by_admin_user_id VARCHAR(36), 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	CONSTRAINT user_invitations_pkey PRIMARY KEY (id), 
	CONSTRAINT user_invitations_created_by_admin_user_id_fkey FOREIGN KEY(created_by_admin_user_id) REFERENCES admin_users (id), 
	CONSTRAINT user_invitations_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE user_tenant_membership (
	id VARCHAR(36) NOT NULL, 
	user_id_hash VARCHAR(200) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	is_primary BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT user_tenant_membership_pkey PRIMARY KEY (id), 
	CONSTRAINT user_tenant_membership_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id), 
	CONSTRAINT user_tenant_membership_user_id_hash_tenant_id_key UNIQUE NULLS DISTINCT (user_id_hash, tenant_id)
);


CREATE TABLE admin_scopes (
	id VARCHAR(36) NOT NULL, 
	admin_user_id VARCHAR(36) NOT NULL, 
	scope_type VARCHAR(20) NOT NULL, 
	reseller_partner_id VARCHAR(36), 
	tenant_id VARCHAR(36), 
	group_id VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT admin_scopes_pkey PRIMARY KEY (id), 
	CONSTRAINT admin_scopes_admin_user_id_fkey FOREIGN KEY(admin_user_id) REFERENCES admin_users (id), 
	CONSTRAINT admin_scopes_group_id_fkey FOREIGN KEY(group_id) REFERENCES groups (id), 
	CONSTRAINT admin_scopes_reseller_partner_id_fkey FOREIGN KEY(reseller_partner_id) REFERENCES reseller_partners (id), 
	CONSTRAINT admin_scopes_tenant_id_fkey FOREIGN KEY(tenant_id) REFERENCES tenants (id)
);


CREATE TABLE group_profiles (
	id VARCHAR(36) NOT NULL, 
	group_id VARCHAR(36) NOT NULL, 
	description TEXT, 
	business_unit VARCHAR(100), 
	owner_name VARCHAR(200), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT group_profiles_pkey PRIMARY KEY (id), 
	CONSTRAINT group_profiles_group_id_fkey FOREIGN KEY(group_id) REFERENCES groups (id)
);


CREATE TABLE user_group_membership (
	id VARCHAR(36) NOT NULL, 
	user_id_hash VARCHAR(200) NOT NULL, 
	group_id VARCHAR(36) NOT NULL, 
	tenant_membership_id VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT user_group_membership_pkey PRIMARY KEY (id), 
	CONSTRAINT user_group_membership_group_id_fkey FOREIGN KEY(group_id) REFERENCES groups (id), 
	CONSTRAINT user_group_membership_tenant_membership_id_fkey FOREIGN KEY(tenant_membership_id) REFERENCES user_tenant_membership (id), 
	CONSTRAINT user_group_membership_user_id_hash_group_id_key UNIQUE NULLS DISTINCT (user_id_hash, group_id)
);


CREATE TABLE user_membership_profiles (
	id VARCHAR(36) NOT NULL, 
	tenant_membership_id VARCHAR(36) NOT NULL, 
	first_name VARCHAR(100), 
	last_name VARCHAR(100), 
	email VARCHAR(200), 
	title VARCHAR(100), 
	utilization_level VARCHAR(50), 
	sessions_count INTEGER NOT NULL, 
	avg_improvement_pct INTEGER, 
	last_activity_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	initial_user_type INTEGER, 
	CONSTRAINT user_membership_profiles_pkey PRIMARY KEY (id), 
	CONSTRAINT user_membership_profiles_tenant_membership_id_fkey FOREIGN KEY(tenant_membership_id) REFERENCES user_tenant_membership (id)
);

CREATE INDEX ix_admin_users_role ON admin_users (role);
CREATE UNIQUE INDEX ix_admin_users_user_id_hash ON admin_users (user_id_hash);
CREATE INDEX ix_auth_mfa_challenges_expires_at ON auth_mfa_challenges (expires_at);
CREATE INDEX ix_auth_mfa_challenges_requested_app ON auth_mfa_challenges (requested_app);
CREATE INDEX ix_auth_mfa_challenges_user_id_hash ON auth_mfa_challenges (user_id_hash);
CREATE INDEX ix_auth_sessions_expires_at ON auth_sessions (expires_at);
CREATE INDEX ix_auth_sessions_user_id_hash ON auth_sessions (user_id_hash);
CREATE UNIQUE INDEX ix_auth_users_email ON auth_users (email);
CREATE INDEX ix_auth_users_user_id_hash ON auth_users (user_id_hash);
CREATE INDEX ix_conversation_folders_user_id_hash ON conversation_folders (user_id_hash);
CREATE INDEX ix_conversation_prompt_scores_conversation_id ON conversation_prompt_scores (conversation_id);
CREATE INDEX ix_conversation_prompt_scores_last_scored_at ON conversation_prompt_scores (last_scored_at);
CREATE INDEX ix_conversation_prompt_scores_user_id_hash ON conversation_prompt_scores (user_id_hash);
CREATE INDEX ix_conversations_folder_id ON conversations (folder_id);
CREATE INDEX ix_conversations_user_id_hash ON conversations (user_id_hash);
CREATE INDEX ix_database_instance_configs_is_active ON database_instance_configs (is_active);
CREATE UNIQUE INDEX ix_database_instance_configs_label ON database_instance_configs (label);
CREATE INDEX ix_feedback_conversation_id ON feedback (conversation_id);
CREATE INDEX ix_feedback_turn_id ON feedback (turn_id);
CREATE INDEX ix_feedback_user_id_hash ON feedback (user_id_hash);
CREATE INDEX ix_platform_managed_llm_configs_is_active ON platform_managed_llm_configs (is_active);
CREATE UNIQUE INDEX ix_platform_managed_llm_configs_label ON platform_managed_llm_configs (label);
CREATE INDEX ix_prompt_transform_requests_conversation_id ON prompt_transform_requests (conversation_id);
CREATE INDEX ix_prompt_transform_requests_session_id ON prompt_transform_requests (session_id);
CREATE INDEX ix_prompt_transform_requests_user_id ON prompt_transform_requests (user_id_hash);
CREATE INDEX ix_prompt_ui_instance_configs_is_active ON prompt_ui_instance_configs (is_active);
CREATE UNIQUE INDEX ix_prompt_ui_instance_configs_label ON prompt_ui_instance_configs (label);
CREATE UNIQUE INDEX ix_reseller_partners_reseller_key ON reseller_partners (reseller_key);
CREATE INDEX ix_service_tier_definitions_is_active ON service_tier_definitions (is_active);
CREATE INDEX ix_service_tier_definitions_scope_type ON service_tier_definitions (scope_type);
CREATE INDEX ix_service_tier_definitions_tier_key ON service_tier_definitions (tier_key);
CREATE INDEX ix_vault_secrets_created_by_admin_user_id ON vault_secrets (created_by_admin_user_id);
CREATE INDEX ix_vault_secrets_provider_type ON vault_secrets (provider_type);
CREATE INDEX ix_vault_secrets_scope_id ON vault_secrets (scope_id);
CREATE INDEX ix_vault_secrets_scope_type ON vault_secrets (scope_type);
CREATE INDEX ix_vault_secrets_secret_kind ON vault_secrets (secret_kind);
CREATE INDEX ix_vault_secrets_secret_ref ON vault_secrets (secret_ref);
CREATE INDEX ix_admin_audit_log_action_type ON admin_audit_log (action_type);
CREATE INDEX ix_admin_audit_log_actor_admin_user_id ON admin_audit_log (actor_admin_user_id);
CREATE INDEX ix_admin_audit_log_created_at ON admin_audit_log (created_at);
CREATE INDEX ix_admin_audit_log_request_id ON admin_audit_log (request_id);
CREATE INDEX ix_admin_audit_log_target_id ON admin_audit_log (target_id);
CREATE INDEX ix_admin_audit_log_target_type ON admin_audit_log (target_type);
CREATE INDEX ix_admin_permissions_admin_user_id ON admin_permissions (admin_user_id);
CREATE INDEX ix_admin_permissions_permission_key ON admin_permissions (permission_key);
CREATE UNIQUE INDEX ix_admin_profiles_admin_user_id ON admin_profiles (admin_user_id);
CREATE INDEX ix_admin_sessions_admin_user_id ON admin_sessions (admin_user_id);
CREATE INDEX ix_admin_sessions_expires_at ON admin_sessions (expires_at);
CREATE INDEX ix_admin_sessions_issued_at ON admin_sessions (issued_at);
CREATE INDEX ix_admin_sessions_revoked_at ON admin_sessions (revoked_at);
CREATE INDEX ix_admin_sessions_user_id_hash ON admin_sessions (user_id_hash);
CREATE INDEX ix_conversation_turns_conversation_id ON conversation_turns (conversation_id);
CREATE INDEX ix_guide_me_sessions_conversation_id ON guide_me_sessions (conversation_id);
CREATE INDEX ix_guide_me_sessions_user_id_hash ON guide_me_sessions (user_id_hash);
CREATE INDEX ix_password_reset_tokens_token_hash ON password_reset_tokens (token_hash);
CREATE INDEX ix_password_reset_tokens_user_id ON password_reset_tokens (user_id);
CREATE INDEX ix_report_export_jobs_requested_by_admin_user_id ON report_export_jobs (requested_by_admin_user_id);
CREATE INDEX ix_report_export_jobs_status ON report_export_jobs (status);
CREATE INDEX ix_reseller_tenant_defaults_default_platform_managed_config_id ON reseller_tenant_defaults (default_platform_managed_config_id);
CREATE UNIQUE INDEX ix_reseller_tenant_defaults_reseller_partner_id ON reseller_tenant_defaults (reseller_partner_id);
CREATE INDEX ix_tenants_reseller_partner_id ON tenants (reseller_partner_id);
CREATE INDEX ix_tenants_status ON tenants (status);
CREATE UNIQUE INDEX ix_tenants_tenant_key ON tenants (tenant_key);
CREATE INDEX ix_groups_tenant_id ON groups (tenant_id);
CREATE INDEX ix_tenant_llm_config_credential_status ON tenant_llm_config (credential_status);
CREATE UNIQUE INDEX ix_tenant_llm_config_tenant_id ON tenant_llm_config (tenant_id);
CREATE UNIQUE INDEX ix_tenant_onboarding_status_tenant_id ON tenant_onboarding_status (tenant_id);
CREATE INDEX ix_tenant_portal_configs_created_by_admin_user_id ON tenant_portal_configs (created_by_admin_user_id);
CREATE INDEX ix_tenant_portal_configs_is_active ON tenant_portal_configs (is_active);
CREATE UNIQUE INDEX ix_tenant_portal_configs_tenant_id ON tenant_portal_configs (tenant_id);
CREATE UNIQUE INDEX ix_tenant_profiles_tenant_id ON tenant_profiles (tenant_id);
CREATE UNIQUE INDEX ix_tenant_runtime_settings_tenant_id ON tenant_runtime_settings (tenant_id);
CREATE INDEX ix_user_invitations_created_by_admin_user_id ON user_invitations (created_by_admin_user_id);
CREATE INDEX ix_user_invitations_email ON user_invitations (email);
CREATE UNIQUE INDEX ix_user_invitations_invite_token_hash ON user_invitations (invite_token_hash);
CREATE INDEX ix_user_invitations_provider_message_id ON user_invitations (provider_message_id);
CREATE INDEX ix_user_invitations_status ON user_invitations (status);
CREATE INDEX ix_user_invitations_tenant_id ON user_invitations (tenant_id);
CREATE INDEX ix_user_invitations_user_id_hash ON user_invitations (user_id_hash);
CREATE INDEX ix_user_tenant_membership_status ON user_tenant_membership (status);
CREATE INDEX ix_user_tenant_membership_tenant_id ON user_tenant_membership (tenant_id);
CREATE INDEX ix_user_tenant_membership_user_id_hash ON user_tenant_membership (user_id_hash);
CREATE INDEX ix_admin_scopes_admin_user_id ON admin_scopes (admin_user_id);
CREATE INDEX ix_admin_scopes_group_id ON admin_scopes (group_id);
CREATE INDEX ix_admin_scopes_reseller_partner_id ON admin_scopes (reseller_partner_id);
CREATE INDEX ix_admin_scopes_scope_type ON admin_scopes (scope_type);
CREATE INDEX ix_admin_scopes_tenant_id ON admin_scopes (tenant_id);
CREATE UNIQUE INDEX ix_group_profiles_group_id ON group_profiles (group_id);
CREATE INDEX ix_user_group_membership_group_id ON user_group_membership (group_id);
CREATE INDEX ix_user_group_membership_user_id_hash ON user_group_membership (user_id_hash);
CREATE UNIQUE INDEX ix_user_membership_profiles_tenant_membership_id ON user_membership_profiles (tenant_membership_id);
