#
# Copyright (c) 2017 BRCK Inc
#

include $(TOPDIR)/rules.mk

PKG_NAME:=local-dashboard
PKG_VERSION:=v0.0.1
PKG_RELEASE:=1
PKG_MAINTAINER:=Murithi Borona <murithi@brck.com>

include $(INCLUDE_DIR)/package.mk

define Build/Compile
endef

define Package/local-dashboard
	SECTION:=config
	CATEGORY:=BRCK
	TITLE:=SupaBRCK Local Management Dashboard
	URL:=http://www.brck.com
	DEPENDS:=+supabrck-core \
			 +supabrck-utils \
		     +python-flask \
			 +python-gunicorn \
			 +nginx
endef

define Package/local-dashboard/description
	SupaBRCK Local Management Dashboard
endef

define Package/local-dashboard/install
	$(INSTALL_DIR) $(1)/etc/nginx/conf.d
	$(INSTALL_DIR) $(1)/etc/bind
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_DIR) $(1)/opt/apps/local-dashboard
	$(INSTALL_DIR) $(1)/opt/apps/local-dashboard/www

	$(CP) $(PKG_BUILD_DIR)/api $(1)/opt/apps/local-dashboard
	$(CP) $(PKG_BUILD_DIR)/brck-local-dashboard/build $(1)/var/www/local-dashboard


	$(INSTALL_CONF) ./install/nginx.localdash.conf $(1)/etc/nginx/conf.d/localdashboard.conf
	$(INSTALL_DATA) ./files/local.brck.com.conf $(1)/etc/bind/db.local.brck.com
	$(INSTALL_BIN) ./install/local-dash-bind.init $(1)/etc/init.d/local-dashboard-bind
	$(INSTALL_BIN) ./install/local-dash-service.init $(1)/etc/init.d/local-dashboard
endef

define Package/local-dashboard/postinst
	#!/bin/sh
	[ -n "$$IPKG_INST_ROOT" ] && exit 0
	pip install -r /opt/apps/local-dashboard/api/prod_requirements.txt

	# Database Migrations
	cd /opt/apps/local-dashboard/api
	FLASK_CONFIG=production FLASK_APP=./local_api/__init__.py flask db upgrade
	FLASK_CONFIG=production python manage.py add_admin_user

	# Restart services
	for init in supabrck-core nginx chilli; do
		/etc/init.d/"$$init" restart 2>/dev/null
	done

	# Enable the service
	for init in /etc/init.d/local-dashboard*; do
		"$$init" enable
		"$$init" start
	done

	exit 0
endef

$(eval $(call BuildPackage,local-dashboard))
