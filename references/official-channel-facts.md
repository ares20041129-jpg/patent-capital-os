# Official Channel Facts

Use this reference before CNIPA filing operations. Verify current official sources again for live production runs.

Checked: 2026-06-01.

## Sources

- CNIPA Patent Business Processing System: https://cponline.cnipa.gov.cn/
- CNIPA XML electronic-file notice: https://www.cnipa.gov.cn/art/2025/11/12/art_75_202551.html
- CNIPA foreign filing secrecy review service page: https://www.cnipa.gov.cn/art/2020/5/26/art_701_14.html
- CNIPA Patent Law page: https://www.cnipa.gov.cn/art/2020/11/23/art_2197_155169.html
- CNIPA rules on regulating patent application conduct, order 77: https://www.cnipa.gov.cn/art/2023/12/21/art_99_189201.html

## Filing System Baseline

The Patent Business Processing System exposes login, registration for natural persons, legal persons, and agencies, patent application/services/payment areas, help documents, tools, and file upload behind login.

The public system page also points users to the official client, XML editor/conversion tooling, document upload, signature verification, and download/help areas.

## XML Baseline

CNIPA's 2025-11-12 notice states that from 2026-01-01, patent electronic files for patent applications, reexamination, invalidation, and related procedures must be submitted in XML format; non-XML electronic files are no longer accepted for the covered scope.

The covered scope includes Chinese national invention, utility model, and design applications, PCT national phase application files, reexamination request files, invalidation request files, and other requests, declarations, observations, corrections, or related filings submitted in covered electronic procedures.

XML files must satisfy CNIPA data standards, except nucleotide or amino-acid sequence listings that use WIPO ST.26.

## Secrecy Review Baseline

For inventions or utility models completed in China and intended for foreign filing or PCT filing, secrecy review must be resolved before the foreign/PCT filing path proceeds.

The legal gate must distinguish:

- China-only filing now, no foreign/PCT path planned.
- China filing now with later foreign/PCT path planned.
- Direct foreign filing.
- PCT filing through CNIPA, which may be treated as a secrecy review request path.

## Non-Abnormal Filing Baseline

CNIPA order 77, effective 2024-01-20, requires patent applications to be based on real inventive activity and good faith.

The workflow must block applications that are generated mainly by random computer generation, fabricated technical effects, copied or simply replaced prior art, obvious patchwork, unreasonable degradation, non-necessary narrowing, maliciously distributed batch filings, false inventor/applicant changes, or other conduct inconsistent with good faith.

## Production Rule

Drafting automation may prepare files. Filing automation may act only when:

- Legal gate passed.
- Exact package hash was approved by counsel/patent agent, or validated by the AI self-filing legal/compliance gate for an eligible applicant self-filing route.
- Applicant authorized filing and fees.
- Official account, signature authority, and automation permission are documented.
- XML/package validation passed.
- Human-only official-system controls are not bypassed.
- Receipt capture and docket creation are ready.
