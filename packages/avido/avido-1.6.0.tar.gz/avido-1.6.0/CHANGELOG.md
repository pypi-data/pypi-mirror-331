# Changelog

## 1.6.0 (2025-03-04)

Full Changelog: [v1.5.1...v1.6.0](https://github.com/Avido-AI/avido-py/compare/v1.5.1...v1.6.0)

### Features

* **client:** allow passing `NotGiven` for body ([#67](https://github.com/Avido-AI/avido-py/issues/67)) ([dbff040](https://github.com/Avido-AI/avido-py/commit/dbff040aab650794b2b187f54aab6a7eed330c1f))
* **client:** send `X-Stainless-Read-Timeout` header ([#61](https://github.com/Avido-AI/avido-py/issues/61)) ([f3d5ada](https://github.com/Avido-AI/avido-py/commit/f3d5adaa193bbdd6bb46e503b6766c8098032063))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#66](https://github.com/Avido-AI/avido-py/issues/66)) ([f06cec7](https://github.com/Avido-AI/avido-py/commit/f06cec7977861737134ca08c1f2ac8ea7f6174ba))
* **client:** mark some request bodies as optional ([dbff040](https://github.com/Avido-AI/avido-py/commit/dbff040aab650794b2b187f54aab6a7eed330c1f))


### Chores

* **docs:** update client docstring ([#71](https://github.com/Avido-AI/avido-py/issues/71)) ([95a18c9](https://github.com/Avido-AI/avido-py/commit/95a18c920783118be874cbe508d74a37a85a7699))
* **internal:** bummp ruff dependency ([#60](https://github.com/Avido-AI/avido-py/issues/60)) ([138796d](https://github.com/Avido-AI/avido-py/commit/138796d10b29fbcb5e9c2fdcedd82e37a730494b))
* **internal:** change default timeout to an int ([#59](https://github.com/Avido-AI/avido-py/issues/59)) ([a064a7e](https://github.com/Avido-AI/avido-py/commit/a064a7edbfa07b104b2f53ecfcdf034003fc0d78))
* **internal:** fix devcontainers setup ([#68](https://github.com/Avido-AI/avido-py/issues/68)) ([dc46c93](https://github.com/Avido-AI/avido-py/commit/dc46c9399295be7459af1171044e697690e4400e))
* **internal:** fix type traversing dictionary params ([#62](https://github.com/Avido-AI/avido-py/issues/62)) ([a0ce66b](https://github.com/Avido-AI/avido-py/commit/a0ce66bc6c2884d7cd567c1b41aa4fb47f592b95))
* **internal:** minor formatting changes ([#57](https://github.com/Avido-AI/avido-py/issues/57)) ([88270e7](https://github.com/Avido-AI/avido-py/commit/88270e75c1cedde3a2fb3fecff44cf0a7654b770))
* **internal:** minor type handling changes ([#63](https://github.com/Avido-AI/avido-py/issues/63)) ([a8487ba](https://github.com/Avido-AI/avido-py/commit/a8487ba24b4618d28ec6ec8023a71d2626dce071))
* **internal:** properly set __pydantic_private__ ([#69](https://github.com/Avido-AI/avido-py/issues/69)) ([8efa58f](https://github.com/Avido-AI/avido-py/commit/8efa58f03391c71351f2a82c9340dc8b028a3598))
* **internal:** remove unused http client options forwarding ([#72](https://github.com/Avido-AI/avido-py/issues/72)) ([b1bea07](https://github.com/Avido-AI/avido-py/commit/b1bea076374e33c5ec34398ddfc1e3a7c0ccc909))
* **internal:** update client tests ([#65](https://github.com/Avido-AI/avido-py/issues/65)) ([d7b4efe](https://github.com/Avido-AI/avido-py/commit/d7b4efe9c16bcfda57bff6a4f834bb4754e664c3))
* minor change to tests ([#64](https://github.com/Avido-AI/avido-py/issues/64)) ([78bb432](https://github.com/Avido-AI/avido-py/commit/78bb432c55b350c8181f2de23c4c8c9141bb84c3))


### Documentation

* update URLs from stainlessapi.com to stainless.com ([#70](https://github.com/Avido-AI/avido-py/issues/70)) ([0dee5e1](https://github.com/Avido-AI/avido-py/commit/0dee5e1df4ac6d13831da1ac4d1e0d1326dfa56a))

## 1.5.1 (2025-01-23)

Full Changelog: [v1.5.0...v1.5.1](https://github.com/Avido-AI/avido-py/compare/v1.5.0...v1.5.1)

### Chores

* Auto updates from Stainless ([#55](https://github.com/Avido-AI/avido-py/issues/55)) ([fdba936](https://github.com/Avido-AI/avido-py/commit/fdba936ca349e8b910f48582601321475f817ba9))
* **internal:** codegen related update ([#51](https://github.com/Avido-AI/avido-py/issues/51)) ([1593c1f](https://github.com/Avido-AI/avido-py/commit/1593c1f362d69fc720212f2fbecfb2bf53782094))
* **internal:** codegen related update ([#53](https://github.com/Avido-AI/avido-py/issues/53)) ([d1d7801](https://github.com/Avido-AI/avido-py/commit/d1d7801b3170ad251b8429e2ff97ce62e294a36a))
* **internal:** minor style changes ([#54](https://github.com/Avido-AI/avido-py/issues/54)) ([c46fc08](https://github.com/Avido-AI/avido-py/commit/c46fc0866d3ff856dc0c86e9bcafcf4bc09757df))

## 1.5.0 (2025-01-16)

Full Changelog: [v1.4.0...v1.5.0](https://github.com/Avido-AI/avido-py/compare/v1.4.0...v1.5.0)

### Features

* **api:** manual updates ([#47](https://github.com/Avido-AI/avido-py/issues/47)) ([6548383](https://github.com/Avido-AI/avido-py/commit/6548383eacc022ffc24490bafec2d78af35aa7b6))
* **api:** manual updates ([#49](https://github.com/Avido-AI/avido-py/issues/49)) ([5f9f703](https://github.com/Avido-AI/avido-py/commit/5f9f7039988e33fa4c901b4f8976e087238564dd))


### Chores

* Auto updates from Stainless ([#45](https://github.com/Avido-AI/avido-py/issues/45)) ([a259a55](https://github.com/Avido-AI/avido-py/commit/a259a55f5e603b8665f0673131f621b96dbfbb8d))
* Auto updates from Stainless ([#48](https://github.com/Avido-AI/avido-py/issues/48)) ([3948dab](https://github.com/Avido-AI/avido-py/commit/3948dabd04d2b221f2304032f3622a05c27a4066))

## 1.4.0 (2025-01-15)

Full Changelog: [v1.3.2...v1.4.0](https://github.com/Avido-AI/avido-py/compare/v1.3.2...v1.4.0)

### Features

* **api:** manual updates ([#42](https://github.com/Avido-AI/avido-py/issues/42)) ([773476a](https://github.com/Avido-AI/avido-py/commit/773476abd23f2e1f0b050390ec8ba1e85f8f83c4))

## 1.3.2 (2025-01-14)

Full Changelog: [v1.3.1...v1.3.2](https://github.com/Avido-AI/avido-py/compare/v1.3.1...v1.3.2)

### Chores

* Auto updates from Stainless ([#39](https://github.com/Avido-AI/avido-py/issues/39)) ([9e6c6d3](https://github.com/Avido-AI/avido-py/commit/9e6c6d3bd3c2cfe20535b9a219ec46666be00e92))

## 1.3.1 (2025-01-13)

Full Changelog: [v1.3.0...v1.3.1](https://github.com/Avido-AI/avido-py/compare/v1.3.0...v1.3.1)

### Chores

* Auto updates from Stainless ([#36](https://github.com/Avido-AI/avido-py/issues/36)) ([d03084d](https://github.com/Avido-AI/avido-py/commit/d03084dbd2a571faf9910d67a5cfa6c72851db01))

## 1.3.0 (2025-01-13)

Full Changelog: [v1.2.1...v1.3.0](https://github.com/Avido-AI/avido-py/compare/v1.2.1...v1.3.0)

### Features

* **api:** manual updates ([#34](https://github.com/Avido-AI/avido-py/issues/34)) ([24c6c02](https://github.com/Avido-AI/avido-py/commit/24c6c028e60f944518d5eb465e0076c124d82944))


### Bug Fixes

* correctly handle deserialising `cls` fields ([#31](https://github.com/Avido-AI/avido-py/issues/31)) ([cf64cb6](https://github.com/Avido-AI/avido-py/commit/cf64cb6b4208c58f5d5eb4fde497ecb88b94c146))


### Chores

* Auto updates from Stainless ([#33](https://github.com/Avido-AI/avido-py/issues/33)) ([3ba6652](https://github.com/Avido-AI/avido-py/commit/3ba665229eebf61bad067d6ae12d47661c4277bc))

## 1.2.1 (2025-01-09)

Full Changelog: [v1.2.0...v1.2.1](https://github.com/Avido-AI/avido-py/compare/v1.2.0...v1.2.1)

### Bug Fixes

* **api:** better support union schemas with common properties ([#29](https://github.com/Avido-AI/avido-py/issues/29)) ([a82b662](https://github.com/Avido-AI/avido-py/commit/a82b6621fe47006d9785f272cec694c969abbc53))


### Chores

* **internal:** codegen related update ([#28](https://github.com/Avido-AI/avido-py/issues/28)) ([d154a7c](https://github.com/Avido-AI/avido-py/commit/d154a7c5e80205982fb5451598d9c617ce156348))


### Documentation

* fix typos ([#26](https://github.com/Avido-AI/avido-py/issues/26)) ([561d54c](https://github.com/Avido-AI/avido-py/commit/561d54cdff97917aaf394ea9431bd063ce8dd3b4))

## 1.2.0 (2025-01-09)

Full Changelog: [v1.1.2...v1.2.0](https://github.com/Avido-AI/avido-py/compare/v1.1.2...v1.2.0)

### Features

* **api:** manual updates ([#20](https://github.com/Avido-AI/avido-py/issues/20)) ([47278ce](https://github.com/Avido-AI/avido-py/commit/47278cee41c08b69fb5e264e57f2274598230b9c))
* **api:** manual updates ([#22](https://github.com/Avido-AI/avido-py/issues/22)) ([a900248](https://github.com/Avido-AI/avido-py/commit/a9002480c138f6dad5e28400c30884abebc0c1c4))
* **api:** manual updates ([#24](https://github.com/Avido-AI/avido-py/issues/24)) ([f9e2a37](https://github.com/Avido-AI/avido-py/commit/f9e2a37037855f0ce8341251a70f0c25f6990f13))


### Chores

* Auto updates from Stainless ([#18](https://github.com/Avido-AI/avido-py/issues/18)) ([11701d6](https://github.com/Avido-AI/avido-py/commit/11701d66996f0c79ea8a4495482716f502263e85))
* Auto updates from Stainless ([#23](https://github.com/Avido-AI/avido-py/issues/23)) ([b07dafb](https://github.com/Avido-AI/avido-py/commit/b07dafb98069279df95a9366718a5e676ac9177d))
* **internal:** version bump ([#21](https://github.com/Avido-AI/avido-py/issues/21)) ([7edecac](https://github.com/Avido-AI/avido-py/commit/7edecac1d660bf41c2239a3b0a1b52b5eb259197))

## 1.1.2 (2025-01-08)

Full Changelog: [v1.1.1...v1.1.2](https://github.com/Avido-AI/avido-py/compare/v1.1.1...v1.1.2)

### Bug Fixes

* **client:** only call .close() when needed ([#16](https://github.com/Avido-AI/avido-py/issues/16)) ([8ac068e](https://github.com/Avido-AI/avido-py/commit/8ac068e5f7f7ba594e490acaea76f70a6f62641c))

## 1.1.1 (2025-01-08)

Full Changelog: [v1.1.0...v1.1.1](https://github.com/Avido-AI/avido-py/compare/v1.1.0...v1.1.1)

### Chores

* add missing isclass check ([#12](https://github.com/Avido-AI/avido-py/issues/12)) ([04e9a0c](https://github.com/Avido-AI/avido-py/commit/04e9a0c380fc9def7bde16e79598e6196e50330b))
* **internal:** codegen related update ([#14](https://github.com/Avido-AI/avido-py/issues/14)) ([be6589a](https://github.com/Avido-AI/avido-py/commit/be6589a08f08db44983e38917aa6a575d722b7df))

## 1.1.0 (2025-01-07)

Full Changelog: [v1.0.0...v1.1.0](https://github.com/Avido-AI/avido-py/compare/v1.0.0...v1.1.0)

### Features

* **api:** manual updates ([#9](https://github.com/Avido-AI/avido-py/issues/9)) ([6cb9ff4](https://github.com/Avido-AI/avido-py/commit/6cb9ff4212a42e7c8226fa1bc44a6148bd932467))

## 1.0.0 (2025-01-06)

Full Changelog: [v0.1.0-alpha.1...v1.0.0](https://github.com/Avido-AI/avido-py/compare/v0.1.0-alpha.1...v1.0.0)

### Chores

* update SDK settings ([#6](https://github.com/Avido-AI/avido-py/issues/6)) ([7514925](https://github.com/Avido-AI/avido-py/commit/7514925d253e9c99cc6f94b054b3a085bc06eed6))

## 0.1.0-alpha.1 (2025-01-06)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/Avido-AI/avido-py/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** update via SDK Studio ([a8a1a3a](https://github.com/Avido-AI/avido-py/commit/a8a1a3a3ab26f5d33038e4fb32911c7030398e86))
* **api:** update via SDK Studio ([5e6cc7c](https://github.com/Avido-AI/avido-py/commit/5e6cc7cb4ccfb1bcb8f70311969319dcd087daa3))
* **api:** update via SDK Studio ([d59c381](https://github.com/Avido-AI/avido-py/commit/d59c3818a8037ea0f62f5562032fe0130bd614ab))
* **api:** update via SDK Studio ([24d4494](https://github.com/Avido-AI/avido-py/commit/24d44943efc49ae7a8effd5c0ca6ee41e2727234))
* **api:** update via SDK Studio ([fac078e](https://github.com/Avido-AI/avido-py/commit/fac078e32794c9b44e05d127906914e075293d94))
* **api:** update via SDK Studio ([4dd8dc7](https://github.com/Avido-AI/avido-py/commit/4dd8dc7e4eda290498f2e356905dc1573e0645b6))
* **api:** update via SDK Studio ([1601603](https://github.com/Avido-AI/avido-py/commit/16016038e1a8a0da4a07056a63125a7580edf94d))
* **api:** update via SDK Studio ([7893ff8](https://github.com/Avido-AI/avido-py/commit/7893ff86f62b0914e1480f27689060327c1b3c6d))
* **api:** update via SDK Studio ([0fcef05](https://github.com/Avido-AI/avido-py/commit/0fcef05a4471dfa6df21806402a1fe122cd8f0d6))
* **api:** update via SDK Studio ([a66c23c](https://github.com/Avido-AI/avido-py/commit/a66c23c7c508ebdc0110ac4fe274807d0ee2b093))
* **api:** update via SDK Studio ([dc17892](https://github.com/Avido-AI/avido-py/commit/dc178922d71b2501ef4c18ea56ce715a3d959dc5))


### Chores

* go live ([#1](https://github.com/Avido-AI/avido-py/issues/1)) ([b92b753](https://github.com/Avido-AI/avido-py/commit/b92b753e80237da9b48b76af67ee57cb1da2ecce))
* go live ([#4](https://github.com/Avido-AI/avido-py/issues/4)) ([2a7def0](https://github.com/Avido-AI/avido-py/commit/2a7def013625d8ea2b7051c9330865bb168bd9d9))
* update SDK settings ([#3](https://github.com/Avido-AI/avido-py/issues/3)) ([7cebf61](https://github.com/Avido-AI/avido-py/commit/7cebf61017cfb04a8a5b3c905c205986902ccc58))
