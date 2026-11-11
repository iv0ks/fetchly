# Changelog

## [1.0.5](https://github.com/iv0ks/fetchly/compare/v1.0.4...v1.0.5) (2026-11-11)


### Refactoring

* enrich listed documents with display metadata ([503e114](https://github.com/iv0ks/fetchly/commit/503e1141520ed601194ee45a804c6285ed3a6c0f))

## [1.0.4](https://github.com/iv0ks/fetchly/compare/v1.0.3...v1.0.4) (2026-11-10)


### Bug Fixes

* **docker:** resolve issues with python path ([bcc6b73](https://github.com/iv0ks/fetchly/commit/bcc6b737a0297eab3b4245040e860bf2a074f465))

## [1.0.3](https://github.com/iv0ks/fetchly/compare/v1.0.2...v1.0.3) (2026-11-10)


### Bug Fixes

* **docker:** apply os security patches to clear fixable cves ([b41cc46](https://github.com/iv0ks/fetchly/commit/b41cc4672c62a20c71e2eaf6e171795017c4011d))


### Build System

* **app:** optimize multi stage images ([714decb](https://github.com/iv0ks/fetchly/commit/714decb4013900d5f5a8bd7a0184860c969d69de))

## [1.0.2](https://github.com/iv0ks/fetchly/compare/v1.0.1...v1.0.2) (2026-11-10)


### Refactoring

* use thematic flag content instead of numbered level ([127418b](https://github.com/iv0ks/fetchly/commit/127418bebd54bfca0622317457fdbe29ee92c5e1))

## [1.0.1](https://github.com/iv0ks/fetchly/compare/v1.0.0...v1.0.1) (2026-11-09)


### Bug Fixes

* **delivery:** tag image as repo:version instead of repo/version ([0029b6a](https://github.com/iv0ks/fetchly/commit/0029b6ad1e0bf6f0644f81e3ec45c28aca6e4430))

## 1.0.0 (2026-11-09)


### Features

* add external stylesheet and styled error page ([e5e2710](https://github.com/iv0ks/fetchly/commit/e5e27106def6d5e463e2ba54c4a60c5a76d6bff9))
* add storage decoy documents and out-of-vault flag ([72b259d](https://github.com/iv0ks/fetchly/commit/72b259d17c6c5a296557e5932551203e5cde5672))
* add vulnerable flask document-vault app ([b3cb526](https://github.com/iv0ks/fetchly/commit/b3cb526d5787203fbd8f6426915082ed0cff34d8))
* seed the flag on startup so the lab works without docker ([b832f21](https://github.com/iv0ks/fetchly/commit/b832f21f0366df39fa28cb63c229fb61dd7a2fd9))


### Bug Fixes

* **release:** declare root package so release-please generates the release PR ([fb9bdbd](https://github.com/iv0ks/fetchly/commit/fb9bdbdc92972501424ef82012088048a7a58a12))
* **release:** resolve release config issues ([8153d8b](https://github.com/iv0ks/fetchly/commit/8153d8b335e32885bfcf1e6236d8cd6238b98c3a))


### Refactoring

* expose documents at GET /docs?name= and resolve paths in the factory ([473910e](https://github.com/iv0ks/fetchly/commit/473910ec64435f9b3eaf03295ea7196a954c460d))
* group lab data (decoys and flag) under lab/ ([1352411](https://github.com/iv0ks/fetchly/commit/13524119be284adb7b60755e3b17fd9987d58cac))
* move app into src/ layout with app factory and external template ([d1cd7ab](https://github.com/iv0ks/fetchly/commit/d1cd7abfebf3e7f1b777b98ca5af6be5e632600d))
* rename package to app/ and entrypoint to main.py ([aa754f5](https://github.com/iv0ks/fetchly/commit/aa754f5f9ea1397184aae2c0f9de6be4263a5d33))
* serve documents from docs/ via /docs/download?file= ([f80051e](https://github.com/iv0ks/fetchly/commit/f80051e24e9ce76491b40cf857a16514bdd38ddd))


### Build System

* adapt docker and tooling config to docs/ layout ([1927df8](https://github.com/iv0ks/fetchly/commit/1927df828e85b22794e6a0ff11975351051fb25c))
* adapt docker image and tooling config to src/ and lab/ layout ([237e2fb](https://github.com/iv0ks/fetchly/commit/237e2fbbc6b1288485b1d5205bab74edcff765e5))
* add hardened multi-stage docker image and compose ([e2678fe](https://github.com/iv0ks/fetchly/commit/e2678feebb1f34d8a939f37066b93e1c79851594))
* create the flag inside the image instead of committing it ([4c3ca84](https://github.com/iv0ks/fetchly/commit/4c3ca84287a6cc9c8fd52a3fb8192e8050c2284b))
* **deps:** bump actions/checkout from 4 to 7 ([#2](https://github.com/iv0ks/fetchly/issues/2)) ([321b73a](https://github.com/iv0ks/fetchly/commit/321b73a57fbc8046233ec60c007f29cd5959181e))
* **deps:** bump actions/setup-python from 5 to 7 ([#1](https://github.com/iv0ks/fetchly/issues/1)) ([0c3d242](https://github.com/iv0ks/fetchly/commit/0c3d24231e8c190b968c66e7ed53f4e4da4ab5c4))
* **deps:** bump docker/build-push-action from 6 to 7 ([#4](https://github.com/iv0ks/fetchly/issues/4)) ([8edbbc6](https://github.com/iv0ks/fetchly/commit/8edbbc6a871985000f5d88ede0c29cf6411529bb))
* **deps:** bump docker/login-action from 3.3.0 to 4.7.0 ([#7](https://github.com/iv0ks/fetchly/issues/7)) ([9721011](https://github.com/iv0ks/fetchly/commit/9721011703ff685b81cfdae94c5560d5468d39d9))
* **deps:** bump flask ([#5](https://github.com/iv0ks/fetchly/issues/5)) ([59ba63e](https://github.com/iv0ks/fetchly/commit/59ba63e4768d98665bead74836848e7f40643f5b))
* **deps:** bump gunicorn from 22.0.0 to 26.2.0 ([#6](https://github.com/iv0ks/fetchly/issues/6)) ([e4615c6](https://github.com/iv0ks/fetchly/commit/e4615c699955a91b14577182502dc6b85dbfd80c))
* make the baked-in flag overridable via --build-arg FLAG ([ab03cb5](https://github.com/iv0ks/fetchly/commit/ab03cb55cd431d27d8b82d55da86642ca2a6643e))
* update docker and tooling config for app/ package layout ([1f47d9e](https://github.com/iv0ks/fetchly/commit/1f47d9e614298cfc3667c903abaaa12e0e6b69c4))
