import requests
import subprocess
import sys

def uninstall_previous_versions():
    """
    دالة لإزالة الإصدارات السابقة من المكتبة.
    """
    package_name = "spider-api"  # استبدل this باسم المكتبة الخاص بك
    try:
        # قائمة بالإصدارات المثبتة
        installed_packages = subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode("utf-8")
        
        # التحقق من وجود المكتبة في القائمة
        if package_name in installed_packages:
            print(f"🔍 تم العثور على إصدارات سابقة من {package_name}. جاري إزالتها...")
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", package_name, "-y"])
            print(f"✅ تم إزالة الإصدارات السابقة من {package_name}.")
        else:
            print(f"ℹ️ لم يتم العثور على إصدارات سابقة من {package_name}.")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء محاولة إزالة الإصدارات السابقة: {e}")

def WormGPT(text):
    """
    دالة لإرسال نص إلى API واستقبال الرد.

    :param text: النص المراد إرساله.
    :return: الرد من API مع تنسيق مخصص.
    """
    # التحقق من أن النص غير فارغ
    if not text:
        return {"response": "You must enter text. You have not entered text."}

    try:
        # إرسال الطلب إلى API
        response = requests.get(f'https://api-production-8dd7.up.railway.app/api?msg={text}')
        response.raise_for_status()  # التحقق من وجود أخطاء في الطلب

        # استخراج الرد من API
        result = response.json().get("response", "No response found in API reply.")

        # تنسيق الرد
        formatted_response = f"""
{result}

┏━━⚇
┃━┃ t.me/spider_XR7
┗━━━━━━━━
        """
        return {"response": formatted_response}

    except requests.exceptions.RequestException as e:
        # في حالة حدوث خطأ في الاتصال
        return {"response": f"An error occurred while connecting to the API: {e}"}
    except KeyError:
        # في حالة عدم وجود مفتاح "response" في الرد
        return {"response": "The API response format is invalid."}
    except Exception as e:
        # في حالة حدوث أي خطأ غير متوقع
        return {"response": f"An unexpected error occurred: {e}"}

# إزالة الإصدارات السابقة قبل التثبيت
uninstall_previous_versions()
