# Úkryty ČR

Statická webová aplikace: stálé úkryty HZS, hustota obyvatel a plochy pro modulární bunkry ve městech ČR.

- `index.html` – celá aplikace (Leaflet z CDN, data se načítají z `data/`).
- `data/registry.json`, `data/cr.json` – národní přehled a registr měst.
- `data/cities/<město>.json.gz` – data města (gzip; aplikace je rozbalí v prohlížeči).

Hosting: Cloudflare Pages (bez build kroku, výstupní adresář = kořen repozitáře), přístup chráněný Cloudflare Access.
Data se generují mimo tento repozitář a nahrávají se sem jen hotové výstupy.
