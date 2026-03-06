.PHONY: setup ios android test clean clean-all help

setup:
	@$(MAKE) -C mobile-app install

ios:
	@$(MAKE) -C mobile-app build-ios

android:
	@$(MAKE) -C mobile-app build-android

clean:
	@$(MAKE) -C mobile-app clean

clean-all:
	@$(MAKE) -C mobile-app clean-all

help:
	@echo "Available targets:"
	@echo "  make setup      - Install Node dependencies"
	@echo "  make ios        - Build Nim backend + iOS app"
	@echo "  make android    - Build Nim backend + Android app"
	@echo "  make clean      - Clean all build artifacts"
	@echo "  make clean-all  - Clean everything including Nim caches"
	@echo ""
	@echo "Sub-project targets:"
	@echo "  make -C mobile-app help"
