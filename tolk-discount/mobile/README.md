# Tolk Discount - Мобильное приложение (Flutter)

Нативное мобильное приложение для iOS и Android с дизайном Liquid Glass.

## Требования

- Flutter SDK >= 3.16.0
- Dart >= 3.2.0
- Xcode >= 15.0 (для iOS)
- Android Studio >= 2023.1 (для Android)

## Быстрый старт

```bash
# Установка зависимостей
flutter pub get

# Запуск в режиме разработки
flutter run

# Запуск на конкретном устройстве
flutter devices  # Показать доступные устройства
flutter run -d <device_id>

# Сборка релизной версии
flutter build apk --release  # Android
flutter build ios --release  # iOS
```

## Архитектура

Приложение использует чистую архитектуру (Clean Architecture) с разделением на слои:

```
lib/
├── main.dart                 # Точка входа
├── app/                      # Конфигурация приложения
│   ├── app.dart
│   ├── routes.dart
│   └── theme.dart
├── core/                     # Базовые компоненты
│   ├── constants/
│   ├── errors/
│   ├── network/
│   ├── storage/
│   └── utils/
├── features/                 # Функциональные модули
│   ├── auth/
│   ├── discounts/
│   ├── profile/
│   ├── collections/
│   └── settings/
├── shared/                   # Переиспользуемые компоненты
│   ├── widgets/
│   └── models/
└── data/                     # Слой данных
    ├── repositories/
    ├── datasources/
    └── models/
```

## Дизайн-система Liquid Glass

### Основные принципы

1. **Прозрачность**: 10-30% opacity фонов
2. **Размытие**: backdrop-filter blur(10-30px)
3. **Границы**: тонкие белые/прозрачные borders (1-2px)
4. **Тени**: мягкие рассеянные тени
5. **Градиенты**: subtle gradient overlays

### Базовые виджеты

#### GlassCard

```dart
import 'dart:ui';
import 'package:flutter/material.dart';

class GlassCard extends StatelessWidget {
  final Widget child;
  final double borderRadius;
  final double blurSigma;
  final Color? backgroundColor;
  final EdgeInsets padding;
  
  const GlassCard({
    super.key,
    required this.child,
    this.borderRadius = 20,
    this.blurSigma = 20,
    this.backgroundColor,
    this.padding = const EdgeInsets.all(16),
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: backgroundColor ?? Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(borderRadius),
            border: Border.all(
              color: Colors.white.withOpacity(0.3),
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 20,
                spreadRadius: 5,
              ),
              BoxShadow(
                color: Colors.white.withOpacity(0.1),
                blurRadius: 10,
                spreadRadius: -5,
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
```

#### GlassButton

```dart
class GlassButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final bool isLoading;
  final GlassButtonVariant variant;
  final IconData? icon;
  
  const GlassButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.isLoading = false,
    this.variant = GlassButtonVariant.primary,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final colors = {
      GlassButtonVariant.primary: Colors.blue,
      GlassButtonVariant.secondary: Colors.grey,
      GlassButtonVariant.danger: Colors.red,
    };
    
    final baseColor = colors[variant]!;
    
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isLoading ? null : onPressed,
            splashColor: baseColor.withOpacity(0.3),
            highlightColor: Colors.transparent,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    baseColor.withOpacity(0.3),
                    baseColor.withOpacity(0.1),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: baseColor.withOpacity(0.5),
                  width: 1.5,
                ),
                boxShadow: [
                  BoxShadow(
                    color: baseColor.withOpacity(0.3),
                    blurRadius: 8,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: isLoading
                  ? SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          baseColor,
                        ),
                      ),
                    )
                  : Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (icon != null) ...[
                          Icon(icon, color: baseColor),
                          const SizedBox(width: 8),
                        ],
                        Text(
                          text,
                          style: TextStyle(
                            color: baseColor,
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
        ),
      ),
    );
  }
}

enum GlassButtonVariant { primary, secondary, danger }
```

#### GlassTextField

```dart
class GlassTextField extends StatelessWidget {
  final TextEditingController? controller;
  final String? labelText;
  final IconData? prefixIcon;
  final bool obscureText;
  final TextInputType? keyboardType;
  final ValueChanged<String>? onChanged;
  final String? errorText;
  
  const GlassTextField({
    super.key,
    this.controller,
    this.labelText,
    this.prefixIcon,
    this.obscureText = false,
    this.keyboardType,
    this.onChanged,
    this.errorText,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.15),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: errorText != null 
                  ? Colors.red.withOpacity(0.5) 
                  : Colors.white.withOpacity(0.3),
              width: 1.5,
            ),
          ),
          child: TextField(
            controller: controller,
            obscureText: obscureText,
            keyboardType: keyboardType,
            onChanged: onChanged,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              labelText: labelText,
              labelStyle: TextStyle(color: Colors.white.withOpacity(0.7)),
              prefixIcon: prefixIcon != null
                  ? Icon(prefixIcon, color: Colors.white.withOpacity(0.7))
                  : null,
              errorText: errorText,
              errorStyle: const TextStyle(color: Colors.redAccent),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 16,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
```

## Тема приложения

```dart
// app/theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      primaryColor: const Color(0xFF3B82F6),
      scaffoldBackgroundColor: const Color(0xFFF0F4F8),
      fontFamily: 'SF Pro Display',
      
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF3B82F6),
        brightness: Brightness.light,
      ),
      
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: Color(0xFF1A1A2E),
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
      ),
      
      cardTheme: CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withOpacity(0.5),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.white.withOpacity(0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 2),
        ),
      ),
      
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
  
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      primaryColor: const Color(0xFF3B82F6),
      scaffoldBackgroundColor: const Color(0xFF0F172A),
      fontFamily: 'SF Pro Display',
      
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF3B82F6),
        brightness: Brightness.dark,
      ),
      
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
      ),
      
      cardTheme: CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withOpacity(0.1),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.white.withOpacity(0.2)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 2),
        ),
      ),
      
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}
```

## Настройка проекта

### pubspec.yaml

```yaml
name: tolk_discount
description: Платформа скидок Tolk - мобильное приложение
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.4.9
  riverpod_annotation: ^2.3.3
  
  # Navigation
  go_router: ^13.0.0
  
  # Network
  dio: ^5.4.0
  retrofit: ^4.0.3
  json_annotation: ^4.8.1
  
  # Local Storage
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  flutter_secure_storage: ^9.0.0
  
  # UI
  cached_network_image: ^3.3.1
  shimmer: ^3.0.0
  flutter_svg: ^2.0.9
  
  # Utils
  intl: ^0.18.1
  url_launcher: ^6.2.2
  share_plus: ^7.2.1
  path_provider: ^2.1.2
  
  # Push Notifications
  firebase_core: ^2.24.2
  firebase_messaging: ^14.7.9
  
  # Biometric Auth
  local_auth: ^2.1.8
  
  # Forms
  formz: ^0.7.0
  
  cupertino_icons: ^1.0.6

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  flutter_lints: ^3.0.1
  build_runner: ^2.4.8
  riverpod_generator: ^2.3.9
  retrofit_generator: ^8.0.6
  json_serializable: ^6.7.1
  hive_generator: ^2.0.1

flutter:
  uses-material-design: true
  
  assets:
    - assets/images/
    - assets/icons/
    - assets/animations/
  
  fonts:
    - family: SF Pro Display
      fonts:
        - asset: assets/fonts/SF-Pro-Display-Regular.otf
        - asset: assets/fonts/SF-Pro-Display-Medium.otf
          weight: 500
        - asset: assets/fonts/SF-Pro-Display-Semibold.otf
          weight: 600
        - asset: assets/fonts/SF-Pro-Display-Bold.otf
          weight: 700
```

## Структура экранов авторизации

### Регистрация по телефону

```dart
// features/auth/screens/phone_registration_screen.dart
class PhoneRegistrationScreen extends ConsumerStatefulWidget {
  const PhoneRegistrationScreen({super.key});

  @override
  ConsumerState<PhoneRegistrationScreen> createState() => _PhoneRegistrationScreenState();
}

class _PhoneRegistrationScreenState extends ConsumerState<PhoneRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  bool _isLoading = false;
  String? _errorText;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              const Color(0xFF667EEA),
              const Color(0xFF764BA2),
              const Color(0xFFF093FB),
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'Tolk Discount',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Лучшие скидки рядом с вами',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
                const SizedBox(height: 48),
                
                GlassCard(
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Text(
                          'Регистрация',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1A1A2E),
                          ),
                        ),
                        const SizedBox(height: 24),
                        
                        GlassTextField(
                          controller: _phoneController,
                          labelText: 'Номер телефона',
                          prefixIcon: Icons.phone_outlined,
                          keyboardType: TextInputType.phone,
                          errorText: _errorText,
                        ),
                        const SizedBox(height: 16),
                        
                        GlassButton(
                          text: 'Получить код',
                          onPressed: _isLoading ? null : _sendSmsCode,
                          isLoading: _isLoading,
                          variant: GlassButtonVariant.primary,
                        ),
                        const SizedBox(height: 16),
                        
                        TextButton(
                          onPressed: () => _navigateToEmailRegistration(),
                          child: Text(
                            'Зарегистрироваться по email',
                            style: TextStyle(
                              color: Colors.blue.withOpacity(0.8),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Future<void> _sendSmsCode() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() {
      _isLoading = true;
      _errorText = null;
    });
    
    try {
      // Вызов API для отправки SMS
      await ref.read(authServiceProvider).sendSmsCode(
        phone: _phoneController.text,
      );
      
      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => SmsVerificationScreen(
              phone: _phoneController.text,
            ),
          ),
        );
      }
    } catch (e) {
      setState(() {
        _errorText = 'Ошибка отправки SMS. Попробуйте позже.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  void _navigateToEmailRegistration() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const EmailRegistrationScreen(),
      ),
    );
  }
}
```

## Оптимизация размера приложения

### 1. Включение ProGuard/R8 (Android)

```properties
# android/app/proguard-rules.pro
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# Retrofit
-keepattributes Signature
-keepattributes Exceptions
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
-dontwarn org.codehaus.mojo.animal_sniffer.IgnoreJRERequirement
-dontwarn javax.annotation.**
-dontwarn kotlin.Unit
-dontwarn retrofit2.KotlinExtensions
-dontwarn retrofit2.KotlinExtensions$*
```

### 2. Разделение APK по ABI

```bash
flutter build apk --split-per-abi
```

### 3. Оптимизация изображений

Используйте формат WebP для изображений:
```bash
cwebp input.png -q 80 -o output.webp
```

### 4. Lazy loading ресурсов

Загружайте изображения и другие ресурсы только когда они нужны.

## Публикация

### Android (Google Play)

```bash
# Создание keystore
keytool -genkey -v -keystore ~/upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload

# Сборка release APK
flutter build appbundle --release

# Загрузка в Google Play Console
```

### iOS (App Store)

```bash
# Сборка IPA
flutter build ipa --release

# Загрузка в App Store Connect через Xcode
```

## Мониторинг и аналитика

### Firebase Crashlytics

```dart
// main.dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  
  // Перехват ошибок
  FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;
  PlatformDispatcher.instance.onError = (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    return true;
  };
  
  runApp(const MyApp());
}
```

## Лицензия

MIT License
