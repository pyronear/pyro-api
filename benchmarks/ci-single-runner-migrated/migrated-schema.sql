--
-- PostgreSQL database dump
--


-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

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

--
-- Name: annotationtype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.annotationtype AS ENUM (
    'WILDFIRE_SMOKE',
    'OTHER_SMOKE',
    'OTHER'
);


--
-- Name: userrole; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'AGENT',
    'USER'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: alerts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alerts (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    lat double precision,
    lon double precision,
    started_at timestamp without time zone NOT NULL,
    last_seen_at timestamp without time zone NOT NULL
);


--
-- Name: alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.alerts_id_seq OWNED BY public.alerts.id;


--
-- Name: alerts_sequences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alerts_sequences (
    alert_id integer NOT NULL,
    sequence_id integer NOT NULL
);


--
-- Name: cameras; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cameras (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    name character varying(100) NOT NULL,
    angle_of_view double precision NOT NULL,
    elevation double precision NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    is_trustable boolean NOT NULL,
    last_active_at timestamp without time zone,
    last_image character varying,
    created_at timestamp without time zone NOT NULL,
    camera_ip character varying,
    device_ip character varying
);


--
-- Name: cameras_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cameras_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cameras_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cameras_id_seq OWNED BY public.cameras.id;


--
-- Name: detections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detections (
    id integer NOT NULL,
    camera_id integer NOT NULL,
    pose_id integer NOT NULL,
    sequence_id integer,
    bucket_key character varying NOT NULL,
    bbox character varying(37) NOT NULL,
    others_bboxes character varying(148),
    created_at timestamp without time zone NOT NULL,
    crop_bucket_key character varying,
    recorded_at timestamp without time zone NOT NULL
);


--
-- Name: detections_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detections_id_seq OWNED BY public.detections.id;


--
-- Name: occlusion_masks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.occlusion_masks (
    id integer NOT NULL,
    pose_id integer NOT NULL,
    mask character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: occlusion_masks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.occlusion_masks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: occlusion_masks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.occlusion_masks_id_seq OWNED BY public.occlusion_masks.id;


--
-- Name: organizations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.organizations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    telegram_id character varying,
    slack_hook character varying
);


--
-- Name: organizations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.organizations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.organizations_id_seq OWNED BY public.organizations.id;


--
-- Name: poses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.poses (
    id integer NOT NULL,
    camera_id integer NOT NULL,
    azimuth double precision NOT NULL,
    patrol_id integer,
    image character varying,
    active boolean DEFAULT true NOT NULL
);


--
-- Name: poses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.poses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: poses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.poses_id_seq OWNED BY public.poses.id;


--
-- Name: sequences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sequences (
    id integer NOT NULL,
    camera_id integer NOT NULL,
    pose_id integer,
    camera_azimuth double precision NOT NULL,
    is_wildfire public.annotationtype,
    sequence_azimuth double precision,
    cone_angle double precision,
    started_at timestamp without time zone NOT NULL,
    last_seen_at timestamp without time zone NOT NULL,
    max_conf double precision,
    temporal_model_score double precision,
    temporal_model_version character varying(32),
    temporal_api_version character varying(32),
    is_validated boolean DEFAULT false NOT NULL,
    validation_due_at timestamp without time zone,
    validation_lease_until timestamp without time zone,
    validation_status character varying(32),
    validation_attempts integer DEFAULT 0 NOT NULL,
    CONSTRAINT ck_sequences_validation_status CHECK (((validation_status)::text = ANY ((ARRAY['model'::character varying, 'fail_open_unavailable'::character varying, 'fail_open_stale'::character varying, 'window_exhausted'::character varying, 'failed'::character varying])::text[])))
);


--
-- Name: sequences_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sequences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sequences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sequences_id_seq OWNED BY public.sequences.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    role public.userrole NOT NULL,
    login character varying(50) NOT NULL,
    hashed_password character varying(70) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: webhooks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.webhooks (
    id integer NOT NULL,
    url character varying NOT NULL
);


--
-- Name: webhooks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.webhooks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: webhooks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.webhooks_id_seq OWNED BY public.webhooks.id;


--
-- Name: alerts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alerts ALTER COLUMN id SET DEFAULT nextval('public.alerts_id_seq'::regclass);


--
-- Name: cameras id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cameras ALTER COLUMN id SET DEFAULT nextval('public.cameras_id_seq'::regclass);


--
-- Name: detections id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections ALTER COLUMN id SET DEFAULT nextval('public.detections_id_seq'::regclass);


--
-- Name: occlusion_masks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occlusion_masks ALTER COLUMN id SET DEFAULT nextval('public.occlusion_masks_id_seq'::regclass);


--
-- Name: organizations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organizations ALTER COLUMN id SET DEFAULT nextval('public.organizations_id_seq'::regclass);


--
-- Name: poses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.poses ALTER COLUMN id SET DEFAULT nextval('public.poses_id_seq'::regclass);


--
-- Name: sequences id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sequences ALTER COLUMN id SET DEFAULT nextval('public.sequences_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: webhooks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.webhooks ALTER COLUMN id SET DEFAULT nextval('public.webhooks_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: alerts_sequences alerts_sequences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alerts_sequences
    ADD CONSTRAINT alerts_sequences_pkey PRIMARY KEY (alert_id, sequence_id);


--
-- Name: cameras cameras_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cameras
    ADD CONSTRAINT cameras_name_key UNIQUE (name);


--
-- Name: cameras cameras_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cameras
    ADD CONSTRAINT cameras_pkey PRIMARY KEY (id);


--
-- Name: detections detections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_pkey PRIMARY KEY (id);


--
-- Name: occlusion_masks occlusion_masks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occlusion_masks
    ADD CONSTRAINT occlusion_masks_pkey PRIMARY KEY (id);


--
-- Name: organizations organizations_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_name_key UNIQUE (name);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: poses poses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.poses
    ADD CONSTRAINT poses_pkey PRIMARY KEY (id);


--
-- Name: sequences sequences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sequences
    ADD CONSTRAINT sequences_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: webhooks webhooks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.webhooks
    ADD CONSTRAINT webhooks_pkey PRIMARY KEY (id);


--
-- Name: webhooks webhooks_url_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.webhooks
    ADD CONSTRAINT webhooks_url_key UNIQUE (url);


--
-- Name: ix_detections_bucket_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_detections_bucket_key ON public.detections USING btree (bucket_key);


--
-- Name: ix_detections_sequence_id_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_detections_sequence_id_created_at ON public.detections USING btree (sequence_id, created_at);


--
-- Name: ix_detections_unassigned_camera_pose_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_detections_unassigned_camera_pose_created_at ON public.detections USING btree (camera_id, pose_id, created_at) WHERE (sequence_id IS NULL);


--
-- Name: ix_sequences_camera_pose_last_seen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sequences_camera_pose_last_seen ON public.sequences USING btree (camera_id, pose_id, last_seen_at);


--
-- Name: ix_sequences_validation_due_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sequences_validation_due_at ON public.sequences USING btree (validation_due_at) WHERE (validation_due_at IS NOT NULL);


--
-- Name: ix_users_login; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_login ON public.users USING btree (login);


--
-- Name: alerts alerts_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: alerts_sequences alerts_sequences_alert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alerts_sequences
    ADD CONSTRAINT alerts_sequences_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES public.alerts(id);


--
-- Name: alerts_sequences alerts_sequences_sequence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alerts_sequences
    ADD CONSTRAINT alerts_sequences_sequence_id_fkey FOREIGN KEY (sequence_id) REFERENCES public.sequences(id);


--
-- Name: cameras cameras_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cameras
    ADD CONSTRAINT cameras_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: detections detections_camera_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_camera_id_fkey FOREIGN KEY (camera_id) REFERENCES public.cameras(id);


--
-- Name: detections detections_pose_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_pose_id_fkey FOREIGN KEY (pose_id) REFERENCES public.poses(id);


--
-- Name: detections detections_sequence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_sequence_id_fkey FOREIGN KEY (sequence_id) REFERENCES public.sequences(id);


--
-- Name: occlusion_masks occlusion_masks_pose_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.occlusion_masks
    ADD CONSTRAINT occlusion_masks_pose_id_fkey FOREIGN KEY (pose_id) REFERENCES public.poses(id);


--
-- Name: poses poses_camera_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.poses
    ADD CONSTRAINT poses_camera_id_fkey FOREIGN KEY (camera_id) REFERENCES public.cameras(id);


--
-- Name: sequences sequences_camera_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sequences
    ADD CONSTRAINT sequences_camera_id_fkey FOREIGN KEY (camera_id) REFERENCES public.cameras(id);


--
-- Name: sequences sequences_pose_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sequences
    ADD CONSTRAINT sequences_pose_id_fkey FOREIGN KEY (pose_id) REFERENCES public.poses(id);


--
-- Name: users users_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- PostgreSQL database dump complete
--


