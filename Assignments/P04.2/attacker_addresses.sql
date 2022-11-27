--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5
-- Dumped by pg_dump version 14.5

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
-- Name: attacker_addresses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.attacker_addresses (
    attacker_index integer NOT NULL,
    attack_address text
);


--
-- Name: attacker_addresses_attacker_index_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.attacker_addresses_attacker_index_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: attacker_addresses_attacker_index_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.attacker_addresses_attacker_index_seq OWNED BY public.attacker_addresses.attacker_index;


--
-- Name: attacker_addresses attacker_index; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attacker_addresses ALTER COLUMN attacker_index SET DEFAULT nextval('public.attacker_addresses_attacker_index_seq'::regclass);

INSERT INTO public.attacker_addresses (attacker_index, attack_address) VALUES (1, 'missilecommand.live:8080');
SELECT pg_catalog.setval('public.attacker_addresses_attacker_index_seq', 1, true);

ALTER TABLE ONLY public.attacker_addresses
    ADD CONSTRAINT attacker_addresses_pkey PRIMARY KEY (attacker_index);



