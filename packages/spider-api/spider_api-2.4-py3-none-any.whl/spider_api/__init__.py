import requests

def WormGPT(text):
    
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
