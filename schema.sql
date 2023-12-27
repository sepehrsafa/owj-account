--
-- PostgreSQL database dump
--

-- Dumped from database version 13.4
-- Dumped by pg_dump version 13.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: account_audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.account_audit_log (
    uuid uuid NOT NULL,
    model_name character varying(255) NOT NULL,
    model_pk character varying(255) NOT NULL,
    type character varying(6) NOT NULL,
    changes jsonb NOT NULL,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    changed_by character varying(255)
);


--
-- Name: TABLE account_audit_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.account_audit_log IS 'Audit Log';


--
-- Name: COLUMN account_audit_log.type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.account_audit_log.type IS 'CREATE: CREATE\nUPDATE: UPDATE\nDELETE: DELETE';


--
-- Name: business_account; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.business_account (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    name character varying(100) NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL
);


--
-- Name: business_account_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.business_account_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: business_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.business_account_id_seq OWNED BY public.business_account.id;


--
-- Name: ipgs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ipgs (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(7) NOT NULL,
    terminal_id character varying(100),
    merchant_id character varying(100),
    merchant_key character varying(100),
    password character varying(100),
    callback_url character varying(100) NOT NULL,
    currency character varying(3) DEFAULT 'IRR'::character varying NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    url character varying(100) NOT NULL
);


--
-- Name: COLUMN ipgs.type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.ipgs.type IS 'SEP: SEP\nNEXTPAY: NEXTPAY';


--
-- Name: COLUMN ipgs.currency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.ipgs.currency IS 'IRR: IRR';


--
-- Name: ipgs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ipgs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ipgs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ipgs_id_seq OWNED BY public.ipgs.id;


--
-- Name: ipgtransaction; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ipgtransaction (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status character varying(11) DEFAULT 'PENDING'::character varying NOT NULL,
    type character varying(100) NOT NULL,
    amount numeric(20,2) DEFAULT 0 NOT NULL,
    currency character varying(3) DEFAULT 'IRR'::character varying NOT NULL,
    card_number character varying(100),
    card_type character varying(100),
    reference_id character varying(100),
    note text,
    ipg_reference_id character varying(100),
    shaparak_reference_id character varying(100),
    trace_number character varying(100),
    token character varying(100),
    ipg_id integer NOT NULL,
    user_id integer NOT NULL,
    wallet_id integer
);


--
-- Name: COLUMN ipgtransaction.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.ipgtransaction.status IS 'SUCCESS: SUCCESS\nFAILED: FAILED\nPENDING: PENDING\nCANCELED: CANCELED\nDISCREPANCY: DISCREPANCY\nUNKNOWN: UNKNOWN\nVERIFYING: VERIFYING';


--
-- Name: COLUMN ipgtransaction.currency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.ipgtransaction.currency IS 'IRR: IRR';


--
-- Name: ipgtransaction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ipgtransaction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ipgtransaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ipgtransaction_id_seq OWNED BY public.ipgtransaction.id;


--
-- Name: user_account; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_account (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    uuid uuid NOT NULL,
    type character varying(18) DEFAULT 'REGULAR_USER'::character varying NOT NULL,
    phone_number character varying(30) NOT NULL,
    email character varying(150),
    first_name character varying(100),
    last_name character varying(110),
    iran_national_id character varying(10),
    iban_number character varying(26),
    is_active boolean DEFAULT true NOT NULL,
    is_buying_allowed boolean DEFAULT true NOT NULL,
    is_phone_number_verified boolean DEFAULT false NOT NULL,
    is_email_verified boolean DEFAULT false NOT NULL,
    is_only_otp_login_allowed boolean DEFAULT true NOT NULL,
    is_2fa_on boolean DEFAULT false NOT NULL,
    otp_hash character varying(300) NOT NULL,
    last_otp_sent timestamp with time zone,
    hashed_password character varying(1000),
    business_id integer
);


--
-- Name: COLUMN user_account.type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.user_account.type IS 'AGENCY_SUPERUSER: AGENCY_SUPERUSER\nAGENCY_USER: AGENCY_USER\nBUSINESS_SUPERUSER: BUSINESS_SUPERUSER\nBUSINESS_USER: BUSINESS_USER\nREGULAR_USER: REGULAR_USER';


--
-- Name: user_account_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_account_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_account_id_seq OWNED BY public.user_account.id;


--
-- Name: user_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_group (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    name character varying(100) NOT NULL,
    permissions jsonb NOT NULL
);


--
-- Name: user_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_group_id_seq OWNED BY public.user_group.id;


--
-- Name: user_group_user_account; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_group_user_account (
    user_group_id integer NOT NULL,
    useraccount_id integer NOT NULL
);


--
-- Name: user_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_tokens (
    jti uuid NOT NULL,
    refresh_token character varying(2000) NOT NULL,
    expire timestamp with time zone NOT NULL,
    user_id integer NOT NULL
);


--
-- Name: wallet_transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wallet_transactions (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    amount numeric(20,2) DEFAULT 0 NOT NULL,
    currency character varying(3) DEFAULT 'IRR'::character varying NOT NULL,
    note text,
    reference character varying(100),
    balance numeric(20,2) DEFAULT 0 NOT NULL,
    preformed_by_id integer NOT NULL,
    wallet_id integer NOT NULL
);


--
-- Name: COLUMN wallet_transactions.currency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.wallet_transactions.currency IS 'IRR: IRR';


--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.wallet_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.wallet_transactions_id_seq OWNED BY public.wallet_transactions.id;


--
-- Name: wallets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wallets (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "limit" numeric(20,2) DEFAULT 0 NOT NULL,
    amount numeric(20,2) DEFAULT 0 NOT NULL,
    currency character varying(3) NOT NULL,
    business_id integer,
    user_id integer NOT NULL
);


--
-- Name: COLUMN wallets.currency; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.wallets.currency IS 'IRR: IRR';


--
-- Name: wallets_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.wallets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wallets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.wallets_id_seq OWNED BY public.wallets.id;


--
-- Name: business_account id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_account ALTER COLUMN id SET DEFAULT nextval('public.business_account_id_seq'::regclass);


--
-- Name: ipgs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipgs ALTER COLUMN id SET DEFAULT nextval('public.ipgs_id_seq'::regclass);


--
-- Name: ipgtransaction id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipgtransaction ALTER COLUMN id SET DEFAULT nextval('public.ipgtransaction_id_seq'::regclass);


--
-- Name: user_account id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_account ALTER COLUMN id SET DEFAULT nextval('public.user_account_id_seq'::regclass);


--
-- Name: user_group id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_group ALTER COLUMN id SET DEFAULT nextval('public.user_group_id_seq'::regclass);


--
-- Name: wallet_transactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallet_transactions ALTER COLUMN id SET DEFAULT nextval('public.wallet_transactions_id_seq'::regclass);


--
-- Name: wallets id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallets ALTER COLUMN id SET DEFAULT nextval('public.wallets_id_seq'::regclass);


--
-- Name: account_audit_log account_audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_audit_log
    ADD CONSTRAINT account_audit_log_pkey PRIMARY KEY (uuid);


--
-- Name: business_account business_account_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.business_account
    ADD CONSTRAINT business_account_pkey PRIMARY KEY (id);


--
-- Name: ipgs ipgs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipgs
    ADD CONSTRAINT ipgs_pkey PRIMARY KEY (id);


--
-- Name: ipgtransaction ipgtransaction_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipgtransaction
    ADD CONSTRAINT ipgtransaction_pkey PRIMARY KEY (id);


--
-- Name: wallets uid_wallets_user_id_7dec3a; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT uid_wallets_user_id_7dec3a UNIQUE (user_id, currency);


--
-- Name: user_account user_account_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_account
    ADD CONSTRAINT user_account_email_key UNIQUE (email);


--
-- Name: user_account user_account_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_account
    ADD CONSTRAINT user_account_phone_number_key UNIQUE (phone_number);


--
-- Name: user_account user_account_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_account
    ADD CONSTRAINT user_account_pkey PRIMARY KEY (id);


--
-- Name: user_account user_account_uuid_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_account
    ADD CONSTRAINT user_account_uuid_key UNIQUE (uuid);


--
-- Name: user_group user_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_group
    ADD CONSTRAINT user_group_name_key UNIQUE (name);


--
-- Name: user_group user_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_group
    ADD CONSTRAINT user_group_pkey PRIMARY KEY (id);


--
-- Name: user_tokens user_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_tokens
    ADD CONSTRAINT user_tokens_pkey PRIMARY KEY (jti);


--
-- Name: wallet_transactions wallet_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transactions_pkey PRIMARY KEY (id);


--
-- Name: wallets wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_pkey PRIMARY KEY (id);


--
-- Name: idx_user_accoun_uuid_fec5eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_accoun_uuid_fec5eb ON public.user_account USING btree (uuid);


--
-- Name: ipgtransaction ipgtransaction_ipg_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipgtransaction
    ADD CONSTRAINT ipgtransaction_ipg_id_fkey FOREIGN KEY (ipg_id) REFERENCES public.ipgs(id) ON DELETE CASCADE;


--
-- Name: ipgtransaction ipgtransaction_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipgtransaction
    ADD CONSTRAINT ipgtransaction_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_account(id) ON DELETE CASCADE;


--
-- Name: ipgtransaction ipgtransaction_wallet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ipgtransaction
    ADD CONSTRAINT ipgtransaction_wallet_id_fkey FOREIGN KEY (wallet_id) REFERENCES public.wallets(id) ON DELETE CASCADE;


--
-- Name: user_account user_account_business_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_account
    ADD CONSTRAINT user_account_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_account(id) ON DELETE CASCADE;


--
-- Name: user_group_user_account user_group_user_account_user_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_group_user_account
    ADD CONSTRAINT user_group_user_account_user_group_id_fkey FOREIGN KEY (user_group_id) REFERENCES public.user_group(id) ON DELETE CASCADE;


--
-- Name: user_group_user_account user_group_user_account_useraccount_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_group_user_account
    ADD CONSTRAINT user_group_user_account_useraccount_id_fkey FOREIGN KEY (useraccount_id) REFERENCES public.user_account(id) ON DELETE CASCADE;


--
-- Name: user_tokens user_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_tokens
    ADD CONSTRAINT user_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_account(id) ON DELETE CASCADE;


--
-- Name: wallet_transactions wallet_transactions_preformed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transactions_preformed_by_id_fkey FOREIGN KEY (preformed_by_id) REFERENCES public.user_account(id) ON DELETE CASCADE;


--
-- Name: wallet_transactions wallet_transactions_wallet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transactions_wallet_id_fkey FOREIGN KEY (wallet_id) REFERENCES public.wallets(id) ON DELETE CASCADE;


--
-- Name: wallets wallets_business_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_account(id) ON DELETE CASCADE;


--
-- Name: wallets wallets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_account(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

