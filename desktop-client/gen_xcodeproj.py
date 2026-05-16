#!/usr/bin/env python3
"""Generate a minimal valid Xcode project.pbxproj for CI detection."""

import os


def make_pbxproj():
    return """// !$*UTF8*$*
{
    archiveVersion = 1;
    classes = {
    };
    objectVersion = 56;
    objects = {
/* Begin PBXBuildFile section */
        A10001 /* AppDelegate.swift in Sources */ = {isa = PBXBuildFile; fileRef = B10001 /* AppDelegate.swift */; };
        A10002 /* SceneDelegate.swift in Sources */ = {isa = PBXBuildFile; fileRef = B10002 /* SceneDelegate.swift */; };
        A10003 /* ViewController.swift in Sources */ = {isa = PBXBuildFile; fileRef = B10003 /* ViewController.swift */; };
        A10004 /* CameraManager.swift in Sources */ = {isa = PBXBuildFile; fileRef = B10004 /* CameraManager.swift */; };
        A10005 /* StreamServer.swift in Sources */ = {isa = PBXBuildFile; fileRef = B10005 /* StreamServer.swift */; };
        A10006 /* NetworkUtils.swift in Sources */ = {isa = PBXBuildFile; fileRef = B10006 /* NetworkUtils.swift */; };
        A10007 /* QRCodeHelper.swift in Sources */ = {isa = PBXBuildFile; fileRef = B10007 /* QRCodeHelper.swift */; };
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
        B10001 /* AppDelegate.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = AppDelegate.swift; sourceTree = \"<group>\"; };
        B10002 /* SceneDelegate.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = SceneDelegate.swift; sourceTree = \"<group>\"; };
        B10003 /* ViewController.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ViewController.swift; sourceTree = \"<group>\"; };
        B10004 /* CameraManager.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = CameraManager.swift; sourceTree = \"<group>\"; };
        B10005 /* StreamServer.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = StreamServer.swift; sourceTree = \"<group>\"; };
        B10006 /* NetworkUtils.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = NetworkUtils.swift; sourceTree = \"<group>\"; };
        B10007 /* QRCodeHelper.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = QRCodeHelper.swift; sourceTree = \"<group>\"; };
        B10008 /* Info.plist */ = {isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = \"<group>\"; };
        B10009 /* Assets.xcassets */ = {isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = \"<group>\"; };
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
        C10001 /* Frameworks */ = {
            isa = PBXFrameworksBuildPhase;
            buildActionMask = 2147483647;
            files = (
            );
            runOnlyForDeploymentPostprocessing = 0;
        };
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
        D10001 = {
            isa = PBXGroup;
            children = (
                D10002 /* RifatCamPro */,
            );
            sourceTree = "<root>";
        };
        D10002 /* RifatCamPro */ = {
            isa = PBXGroup;
            children = (
                B10001 /* AppDelegate.swift */,
                B10002 /* SceneDelegate.swift */,
                B10003 /* ViewController.swift */,
                B10004 /* CameraManager.swift */,
                B10005 /* StreamServer.swift */,
                B10006 /* NetworkUtils.swift */,
                B10007 /* QRCodeHelper.swift */,
                B10008 /* Info.plist */,
                B10009 /* Assets.xcassets */,
            );
            path = "ios-app/RifatCamPro";
            sourceTree = SOURCE_ROOT;
        };
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
        E10001 /* RifatCamPro */ = {
            isa = PBXNativeTarget;
            buildConfigurationList = F20001 /* Build config list for RifatCamPro */;
            buildPhases = (
                G10001 /* Sources */,
                C10001 /* Frameworks */,
                H10001 /* Resources */,
            );
            buildRules = (
            );
            dependencies = (
            );
            name = RifatCamPro;
            productName = RifatCamPro;
        };
/* End PBXNativeTarget section */

/* Begin PBXProject section */
        P10001 /* Project object */ = {
            isa = PBXProject;
            attributes = {
                BuildIndependentTargetsInParallel = 1;
                LastSwiftUpdateCheck = 1500;
                LastUpgradeCheck = 1500;
            };
            buildConfigurationList = F10001 /* Build config list for project */;
            compatibilityVersion = "Xcode 14.0";
            developmentRegion = en;
            hasScannedForEncodings = 0;
            knownRegions = (
                en,
                Base,
            );
            mainGroup = D10001;
            productRefGroup = D10001;
            projectDirPath = "";
            projectRoot = "";
            targets = (
                E10001 /* RifatCamPro */,
            );
        };
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
        H10001 /* Resources */ = {
            isa = PBXResourcesBuildPhase;
            buildActionMask = 2147483647;
            files = (
            );
            runOnlyForDeploymentPostprocessing = 0;
        };
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
        G10001 /* Sources */ = {
            isa = PBXSourcesBuildPhase;
            buildActionMask = 2147483647;
            files = (
                A10001 /* AppDelegate.swift in Sources */,
                A10002 /* SceneDelegate.swift in Sources */,
                A10003 /* ViewController.swift in Sources */,
                A10004 /* CameraManager.swift in Sources */,
                A10005 /* StreamServer.swift in Sources */,
                A10006 /* NetworkUtils.swift in Sources */,
                A10007 /* QRCodeHelper.swift in Sources */,
            );
            runOnlyForDeploymentPostprocessing = 0;
        };
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
        I10001 /* Debug */ = {
            isa = XCBuildConfiguration;
            buildSettings = {
                ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
                CODE_SIGN_STYLE = Automatic;
                CURRENT_PROJECT_VERSION = 1;
                GENERATE_INFOPLIST_FILE = NO;
                INFOPLIST_FILE = "ios-app/RifatCamPro/Info.plist";
                IPHONEOS_DEPLOYMENT_TARGET = 15.0;
                MARKETING_VERSION = 1.0.0;
                PRODUCT_BUNDLE_IDENTIFIER = com.rifatcam.pro;
                PRODUCT_NAME = "$(TARGET_NAME)";
                SWIFT_VERSION = 5.0;
                TARGETED_DEVICE_FAMILY = "1,2";
            };
            name = Debug;
        };
        I10002 /* Release */ = {
            isa = XCBuildConfiguration;
            buildSettings = {
                ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
                CODE_SIGN_STYLE = Automatic;
                CURRENT_PROJECT_VERSION = 1;
                GENERATE_INFOPLIST_FILE = NO;
                INFOPLIST_FILE = "ios-app/RifatCamPro/Info.plist";
                IPHONEOS_DEPLOYMENT_TARGET = 15.0;
                MARKETING_VERSION = 1.0.0;
                PRODUCT_BUNDLE_IDENTIFIER = com.rifatcam.pro;
                PRODUCT_NAME = "$(TARGET_NAME)";
                SWIFT_VERSION = 5.0;
                TARGETED_DEVICE_FAMILY = "1,2";
            };
            name = Release;
        };
        I10003 /* Debug */ = {
            isa = XCBuildConfiguration;
            buildSettings = {
                ALWAYS_SEARCH_USER_PATHS = NO;
                CLANG_ANALYZER_NONNULL = YES;
                CLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
                CLANG_ENABLE_MODULES = YES;
                CLANG_ENABLE_OBJC_ARC = YES;
                COPY_PHASE_STRIP = NO;
                DEBUG_INFORMATION_FORMAT = dwarf;
                ENABLE_STRICT_OBJC_MSGSEND = YES;
                ENABLE_TESTABILITY = YES;
                GCC_DYNAMIC_NO_PIC = NO;
                GCC_OPTIMIZATION_LEVEL = 0;
                GCC_PREPROCESSOR_DEFINITIONS = (
                    "DEBUG=1",
                    "$(inherited)",
                );
                IPHONEOS_DEPLOYMENT_TARGET = 15.0;
                MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
                ONLY_ACTIVE_ARCH = YES;
                SDKROOT = iphoneos;
                SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
                SWIFT_OPTIMIZATION_LEVEL = "-Onone";
            };
            name = Debug;
        };
        I10004 /* Release */ = {
            isa = XCBuildConfiguration;
            buildSettings = {
                ALWAYS_SEARCH_USER_PATHS = NO;
                CLANG_ANALYZER_NONNULL = YES;
                CLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
                CLANG_ENABLE_MODULES = YES;
                COPY_PHASE_STRIP = NO;
                DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
                ENABLE_NS_ASSERTIONS = NO;
                ENABLE_STRICT_OBJC_MSGSEND = YES;
                GCC_OPTIMIZATION_LEVEL = s;
                IPHONEOS_DEPLOYMENT_TARGET = 15.0;
                MTL_ENABLE_DEBUG_INFO = NO;
                SDKROOT = iphoneos;
                SWIFT_COMPILATION_MODE = wholemodule;
                SWIFT_OPTIMIZATION_LEVEL = "-O";
                VALIDATE_PRODUCT = YES;
            };
            name = Release;
        };
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
        F10001 /* Build config list for project */ = {
            isa = XCConfigurationList;
            buildConfigurations = (
                I10003 /* Debug */,
                I10004 /* Release */,
            );
            defaultConfigurationIsVisible = 0;
            defaultConfigurationName = Release;
        };
        F20001 /* Build config list for RifatCamPro */ = {
            isa = XCConfigurationList;
            buildConfigurations = (
                I10001 /* Debug */,
                I10002 /* Release */,
            );
            defaultConfigurationIsVisible = 0;
            defaultConfigurationName = Release;
        };
/* End XCConfigurationList section */
    };
    rootObject = P10001 /* Project object */;
}
"""


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xcodeproj_dir = os.path.join(base, "RifatCamPro.xcodeproj")
    os.makedirs(xcodeproj_dir, exist_ok=True)
    pbxproj_path = os.path.join(xcodeproj_dir, "project.pbxproj")
    with open(pbxproj_path, "w") as f:
        f.write(make_pbxproj())
    print(f"Created {pbxproj_path}")


if __name__ == "__main__":
    main()
