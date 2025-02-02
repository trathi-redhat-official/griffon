#!/usr/bin/env bash

set -x

# primitive smoke test

# service queries
#griffon service component-manifest --purl "pkg:oci/ubi8-minimal-container@sha256:7679eaafa608171dd159a91529804d06fa0fbc16a2ea7f046a592a5d8e22c649?repository_url=registry.redhat.io/ubi8-minimal&tag=8.8-315"
griffon service components-affected-by-flaw CVE-2023-25166 --type NPM
griffon service components-contain-component --purl "pkg:rpm/redhat/zlib@1.2.11-21.el8_7?arch=x86_64"
griffon service product-components --ofuri o:redhat:openshift:4.8.z
griffon service product-components rhel-9.0.0.z
griffon service products-contain-component is-svg
griffon service product-manifest ansible_automation_platform-2.2
#griffon service product-summary --ofuri o:redhat:rhel:8.7.0.z
griffon service product-summary ansible_automation_platform-2.2
griffon service products-affected-by-flaw CVE-2023-25166

griffon --format text service products-contain-component "^webkitgtk(\d)$"
griffon --format text service components-affected-by-flaw CVE-2023-25166
griffon --format text service products-contain-component nmap
griffon service products-contain-component --purl "pkg:rpm/curl@7.29.0"

griffon service products-contain-component webkitgtk --search-related-url --search-latest --search-all

griffon service component-summary curl
griffon service products-contain-component --search-community --search-all curl
griffon -vvv service products-contain-component -a libtiff

# reports
griffon service report-affects

# products
griffon entities component-registry product-streams get pipelines-1.6.2
griffon entities component-registry product-streams list ansible
griffon entities component-registry products list --limit 1000
griffon entities component-registry product-versions list ansible


# components
griffon entities component-registry components list curl
griffon entities component-registry components list curl --namespace UPSTREAM
griffon entities component-registry components get --purl "pkg:rpm/redhat/vim@8.2.2637-16.el9_0.3?arch=src&epoch=2"
griffon entities component-registry components manifest --purl "pkg:rpm/curl@7.76.1"
griffon entities component-registry components list --ofuri o:redhat:ansible_automation_platform:2.2 --type OCI
griffon --format text entities component-registry components list curl

# flaws
griffon entities osidb flaws get --id CVE-2023-25166
griffon entities osidb flaws list --state NEW --impact CRITICAL

# affects
griffon entities osidb affects list --affectedness AFFECTED --impact CRITICAL

# trackers
griffon entities osidb trackers list --help

# manage
griffon entities component-registry admin health
griffon entities osidb admin health

# plugins
griffon plugins go_vuln get --cve-id CVE-2018-16873
griffon plugins osv query-by-commit-hash --commit_hash 6879efc2c1596d11a6a6ad296f80063b558d5e0f
