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
-- Name: fleet_overview; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fleet_overview (
    fleet_num numeric,
    fleet_reference_point public.geometry,
    bearing numeric
);


--
-- Data for Name: fleet_overview; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.fleet_overview (fleet_num, fleet_reference_point, bearing) VALUES (0, '0101000020E6100000114BFC32918223C0009714B6DAC24840', 3.35903145184685);


--
-- PostgreSQL database dump complete
--

