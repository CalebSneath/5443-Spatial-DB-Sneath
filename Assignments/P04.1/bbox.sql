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
-- Name: bbox; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bbox (
    bbox_geom public.geometry,
    bbox_min_spawn public.geometry,
    bbox_max_spawn public.geometry
);


--
-- Data for Name: bbox; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.bbox (bbox_geom, bbox_min_spawn, bbox_max_spawn) VALUES ('010300000001000000050000009365F3FE60A024C01814DDE5E81549408CC33635121F20C01814DDE5E81549408CC33635121F20C050153A4C875F48409365F3FE60A024C050153A4C875F48409365F3FE60A024C01814DDE5E8154940', '0103000020E610000001000000210000008A15F9EBD1CD21C0B5940B19B8BA4840A747B39F9FD021C05D75295C9AB348401CD02C26EDD821C0A5696BA1C2AC4840394F9DD068E621C015A3383A74A64840FB06C0F98DF821C05051F630EDA048400F4EC91EAA0E22C05FA3ADE6639C4840516894BBE32722C0988311FC0499484031978CA6424322C07B21739AF19648409014159AB95F22C0F394842D3E964840EE919D8D307C22C07B21739AF1964840CFC095788F9722C0988311FC0499484011DB6015C9B022C05FA3ADE6639C484025226A3AE5C622C05051F630EDA04840E7D98C630AD922C015A3383A74A648400459FD0D86E622C0A5696BA1C2AC484079E17694D3EE22C05D75295C9AB3484096133148A1F122C0B5940B19B8BA484079E17694D3EE22C00DB4EDD5D5C148400459FD0D86E622C0C5BFAB90ADC84840E7D98C630AD922C05586DEF7FBCE484025226A3AE5C622C01AD8200183D4484011DB6015C9B022C00B86694B0CD94840CFC095788F9722C0D2A505366BDC4840EF919D8D307C22C0EF07A4977EDE48409014159AB95F22C07794920432DF484031978CA6424322C0EF07A4977EDE4840516894BBE32722C0D2A505366BDC48400F4EC91EAA0E22C00B86694B0CD94840FB06C0F98DF821C01AD8200183D44840394F9DD068E621C05586DEF7FBCE48401CD02C26EDD821C0C5BFAB90ADC84840A747B39F9FD021C00DB4EDD5D5C148408A15F9EBD1CD21C0B5940B19B8BA4840', '0103000020E61000000100000021000000C1165652701721C0B5940B19B8BA48408507B926BF1D21C030CE0E30B5AA48408C7A4A956D3021C0D233E3CB4F9B48408C98C7D4C34E21C00DF5B0631F8D484001B65571977721C011BDDB8EAF804840EE95AAC456A921C0B435B8A77A7648400291736518E221C034EED817E56E48407BFA21F6AD1F22C07291347C396A48409014159AB95F22C041D51BC7A5684840A52E083EC59F22C07291347C396A48401E98B6CE5ADD22C034EED817E56E484031937F6F1C1623C0B435B8A77A7648401F73D4C2DB4723C011BDDB8EAF8048409490625FAF7023C00DF5B0631F8D484094AEDF9E058F23C0D233E3CB4F9B48409B21710DB4A123C030CE0E30B5AA48405F12D4E102A823C0B5940B19B8BA48409B21710DB4A123C03A5B0802BBCA484094AEDF9E058F23C098F5336620DA48409490625FAF7023C05D3466CE50E848401F73D4C2DB4723C0596C3BA3C0F4484031937F6F1C1623C0B6F35E8AF5FE48401E98B6CE5ADD22C0363B3E1A8B064940A52E083EC59F22C0F897E2B5360B49409014159AB95F22C02954FB6ACA0C49407BFA21F6AD1F22C0F897E2B5360B49400291736518E221C0363B3E1A8B064940EF95AAC456A921C0B6F35E8AF5FE484001B65571977721C0596C3BA3C0F448408C98C7D4C34E21C05D3466CE50E848408C7A4A956D3021C099F5336620DA48408507B926BF1D21C03A5B0802BBCA4840C1165652701721C0B5940B19B8BA4840');


--
-- PostgreSQL database dump complete
--

