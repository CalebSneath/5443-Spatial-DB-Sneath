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
-- Name: ship_shapes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ship_shapes (
    ship_id numeric,
    ship_polygon public.geometry
);


--
-- Data for Name: ship_shapes; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (0, '0103000020E61000000100000005000000114BFC32918223C0009714B6DAC248402295E6D7068223C0DAF7FFBC00C3484091C2B3E6DF8123C0298948FCFCC24840E44AB4416A8223C09C1B5DF5D6C24840114BFC32918223C0009714B6DAC24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (3, '0103000020E61000000100000005000000B862E00D108423C0411BA790C5C24840FD9D1D5FA18323C0058798FCE3C2484028929BC6838323C0E1A37322E1C24840B5765175F28323C0653082B6C2C24840B862E00D108423C0411BA790C5C24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (6, '0103000020E610000001000000050000005F7AC4E88E8523C0829F396BB0C24840956D9D8E048523C08C8F2572D6C24840A1C6AD9DDD8423C0BF126EB1D2C2484033A6BFF7678523C0011682AAACC248405F7AC4E88E8523C0829F396BB0C24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (9, '0103000020E610000001000000050000000692A8C30D8723C0C323CC459BC24840C5B23FB2A38623C015DE3E6DB8C2484068892F8B848623C07B2DAC6CB5C24840CB6B8B9CEE8623C05D6B394598C248400692A8C30D8723C0C323CC459BC24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (10, '0103000020E61000000100000005000000BE2C15F8C98223C0BFD151F31AC3484049E883E45F8223C0B640C31A38C348403283D1BC408223C031B2301A35C3484016CA55D0AA8223C06E3BBFF217C34840BE2C15F8C98223C0BFD151F31AC34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (13, '0103000020E610000001000000050000000147F9D2488423C04E54E4CD05C34840E214BBCAA28323C0775BC86F33C34840B3DA9E80728323C0AD567EC82EC34840C788BD88188423C09A3C9A2601C348400147F9D2488423C04E54E4CD05C34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (16, '0103000020E61000000100000005000000A75EDDADC78523C0E8D376A8F0C24840111D6FA1CE8423C01CEF411B35C34840A11704FA868423C0D6DF88332EC348403F332C06808523C0879ABDC0E9C24840A75EDDADC78523C0E8D376A8F0C24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (19, '0103000020E61000000100000005000000B073C188468723C08D500983DBC248406C032A7D4D8623C0B5ECD4F51FC3484076CAFCD5058623C073D01B0E19C3484066154EE1FE8623C0300A509BD4C24840B073C188468723C08D500983DBC24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (20, '0103000020E61000000100000005000000650E2EBD028323C0780C8F305BC3484068E0A421108223C0FB1E0DDD9DC348403328CC07CA8123C0D620C21B97C34840047B12A3BC8223C032E6436F54C34840650E2EBD028323C0780C8F305BC34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (23, '0103000020E610000001000000050000001A331298818423C0E68C210B46C34840F468C0746B8423C0210CB9204CC3484096562A8D608423C05814B9134BC34840D12D7BB0768423C08B9421FE44C348401A331298818423C0E68C210B46C34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (24, '0103000020E61000000100000005000000BE9EEA981D8523C0265A461D5FC3484094308275078523C0D1CBDD3265C3484043F7E08DFC8423C05ED6DD2564C348407F7248B1128523C0236446105EC34840BE9EEA981D8523C0265A461D5FC34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (1, '0103000020E61000000100000005000000CAC3D4332D8323C0766039C8F3C24840759131D8A28223C06B6C24CF19C34840C7ECD6E67B8223C019066D0E16C348403FF16442068323C06FED8107F0C24840CAC3D4332D8323C0766039C8F3C24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (2, '0103000020E61000000100000005000000ADCB20D2AC8323C08B8CBFBBECC24840CF32AD223E8323C03C8EB0270BC348402BDFFB89208323C00AB58B4D08C34840A59762398F8323C09FAB9AE1E9C24840ADCB20D2AC8323C08B8CBFBBECC24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (4, '0103000020E6100000010000000500000071DBB80EAC8423C0B7E4CBA2DEC24840EB8D2CFC418423C038F03DCAFBC2484064CDC6D4228423C09951ABC9F8C24840B01D46E78C8423C04E3E39A2DBC2484071DBB80EAC8423C0B7E4CBA2DEC24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (5, '0103000020E6100000010000000500000054E304AD2B8523C0CD105296D7C24840D514979AC18423C0962EC4BDF4C2484023493A73A28423C0158E31BDF1C24840741A9B850C8523C08168BF95D4C2484054E304AD2B8523C0CD105296D7C24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (7, '0103000020E6100000010000000500000018F39CE92A8623C0F8685E7DC9C24840856CE88EA08523C01F044A84EFC248402EF4D09D798523C0B08F92C3EBC248404B4D70F8038623C0D3E7A6BCC5C2484018F39CE92A8623C0F8685E7DC9C24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (8, '0103000020E61000000100000005000000FAFAE887AA8623C00E95E470C2C24840FFA8D675408623C0BAE95698DFC24840ACBB944E218623C09643C497DCC2484099109A608B8623C01EE75170BFC24840FAFAE887AA8623C00E95E470C2C24840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (11, '0103000020E6100000010000000500000075A5EDF8658323C0339B760534C34840022F3848F78223C0D5DB667152C34840EBCB30AFD98223C0B41442974FC348408E61D95F488323C05BCC512B31C3484075A5EDF8658323C0339B760534C34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (12, '0103000020E6100000010000000500000058AD3997E58323C048C7FCF82CC3484006B5533A5B8323C09D11E7FF52C3484052389E48348323C060BE2F3F4FC3484045026FA5BE8323C05467453829C3484058AD3997E58323C048C7FCF82CC34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (14, '0103000020E610000001000000050000001CBDD1D3E48423C0741F09E01EC3484060F38DC5EB8323C0CD20D35263C34840C3DA9B1DA48323C0DF2D1A6B5CC348401B7D992B9D8423C06C0250F817C348401CBDD1D3E48423C0741F09E01EC34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (15, '0103000020E61000000100000005000000FFC41D72648523C0894B8FD317C3484076432FD9718423C031EE0E805AC34840662817C02B8423C09DC7C3BE53C34840B9D0C2581E8523C0D4FC431211C34840FFC41D72648523C0894B8FD317C34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (17, '0103000020E61000000100000005000000C3D4B5AE638623C0B5A39BBA09C348408A2A12FAA18523C090F777F73EC348403B4211E6698523C04B05099039C3484055398A9A2B8623C0D1972C5304C34840C3D4B5AE638623C0B5A39BBA09C34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (18, '0103000020E61000000100000005000000A5DC014DE38623C0CACF21AE02C3484053CA41EC058623C089CDF5853FC348404D77780EC68523C081D8615E39C34840D0F5006FA38623C065B98D86FCC24840A5DC014DE38623C0CACF21AE02C34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (21, '0103000020E61000000100000005000000178706BE9E8323C0E5D5B34274C348400F008B9A888323C01C3C4B587AC34840A35EE0B27D8323C0A5484B4B79C34840B9F25AD6938323C0DCE1B33573C34840178706BE9E8323C0E5D5B34274C34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (22, '0103000020E61000000100000005000000FA8E525C1E8423C0FB013A366DC348409565DD38088423C0036CD14B73C34840E2E63551FD8323C0E477D13E72C34840571DAA74138423C04A0D3A296CC34840FA8E525C1E8423C0FB013A366DC34840');
INSERT INTO public.ship_shapes (ship_id, ship_polygon) VALUES (25, '0103000020E61000000100000005000000A0A636379D8523C03C86CC1058C348400C96D413878523C0B8FB63265EC348406F7F362C7C8523C09D0564195DC34840139D974F928523C0918FCC0357C34840A0A636379D8523C03C86CC1058C34840');


--
-- Name: ship_shape_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ship_shape_index ON public.ship_shapes USING gist (ship_polygon);


--
-- PostgreSQL database dump complete
--

