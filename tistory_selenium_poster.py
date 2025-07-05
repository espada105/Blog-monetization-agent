from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import sys
import os
from selenium.webdriver.common.action_chains import ActionChains

# 마크다운을 HTML로 변환 (간단 변환)
def markdown_to_html(md, json_data=None):
    html = md
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    html = html.replace('\n', '<br>\n')
    html = re.sub(r'<br>\n<br>\n', '</p>\n<p>', html)
    html = f'<p>{html}</p>'

    # JSON 데이터가 있으면 본문에 반드시 포함
    if json_data:
        try:
            import json
            json_str = json.dumps(json_data, ensure_ascii=False)
            html += f'<pre><code>{json_str}</code></pre>'
        except Exception as e:
            print(f"⚠️ JSON 데이터를 HTML에 포함하는 중 오류 발생: {e}")

    return html

# 티스토리 셀레니움 자동 포스팅 함수
def tistory_post_with_selenium(
    markdown_file,
    blog_url,
    category_name="IT",
    tags="BBC뉴스,글로벌트렌드,기술동향",
    headless=False,
    kakao_email=None,
    kakao_password=None,
    json_file=None # 추가된 인자
):
    # 1. 마크다운 파일 읽기
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    title = ""
    body_lines = []
    for line in lines:
        if line.startswith('# ') and not title:
            title = line[2:].strip()
        else:
            body_lines.append(line)
    if not title:
        title = os.path.basename(markdown_file).replace('.md', '')
    body = '\n'.join(body_lines).strip()

    # json_file 인자가 있으면 json_data로 로드
    json_data = None
    if json_file:
        import json
        try:
            with open(json_file, 'r', encoding='utf-8') as jf:
                json_data = json.load(jf)
            print(f"✅ JSON 파일 로드 완료: {json_file}")
        except Exception as e:
            print(f"⚠️ JSON 파일 로드 실패: {e}")
            json_data = None

    # JSON 데이터가 있으면 본문에 반드시 포함
    html_body = markdown_to_html(body, json_data)

    # 2. 셀레니움 브라우저 옵션
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1200,900')
    from selenium.webdriver.chrome.service import Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 3. 카카오 자동 로그인
    if kakao_email and kakao_password:
        print("🔐 카카오 자동 로그인 시도 중...")
        try:
            # 티스토리 로그인 페이지로 이동
            driver.get("https://www.tistory.com/auth/login?redirectUrl=https%3A%2F%2Faigent-hong.tistory.com%2Fmanage%2Fnewpost%2F")
            time.sleep(5)  # 페이지 로딩 대기 시간 증가
            
            # 페이지 로딩 확인
            print(f"현재 페이지: {driver.current_url}")
            
            # 카카오 로그인 버튼 찾기 및 클릭
            print("🔍 카카오 로그인 버튼 찾는 중...")
            kakao_login_button = None
            
            # React 앱이 로드될 때까지 대기
            wait = WebDriverWait(driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button, a, div[role='button']"))
            )
            
            # 페이지 소스 확인 (디버깅용)
            print("현재 페이지 소스 일부:")
            print(driver.page_source[:1000])
            
            # 다양한 방법으로 카카오 로그인 버튼 찾기
            selectors_to_try = [
                "//button[contains(text(), '카카오')]",
                "//a[contains(text(), '카카오')]",
                "//*[contains(text(), '카카오계정')]",
                "//*[contains(text(), '카카오') and contains(text(), '로그인')]",
                "//button[contains(@class, 'kakao')]",
                "//a[contains(@class, 'kakao')]",
                "//div[contains(@class, 'kakao')]",
                "//*[contains(text(), '카카오계정으로 로그인')]",
                "//*[contains(text(), '카카오 로그인')]"
            ]
            
            for selector in selectors_to_try:
                try:
                    kakao_login_button = driver.find_element(By.XPATH, selector)
                    print(f"✅ 카카오 로그인 버튼 발견 (선택자: {selector})")
                    break
                except:
                    continue
            
            if kakao_login_button:
                kakao_login_button.click()
                time.sleep(3)  # 카카오 로그인 페이지 로딩 대기
                print("✅ 카카오 로그인 버튼 클릭 완료")
            else:
                raise Exception("카카오 로그인 버튼을 찾을 수 없습니다")
            
            # 카카오 로그인 페이지의 이메일 입력 필드 찾기
            print("🔍 이메일 입력 필드 찾는 중...")
            email_input = None
            
            # 카카오 로그인 페이지 로딩 대기
            try:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[placeholder*='이메일'], input[placeholder*='아이디'], input[name='email']"))
                )
            except:
                print("이메일 입력 필드 대기 시간 초과, 직접 찾기 시도...")
            
            # 다양한 방법으로 이메일 입력 필드 찾기
            email_selectors = [
                "input[type='email']",
                "input[placeholder*='이메일']",
                "input[placeholder*='아이디']",
                "input[name='email']",
                "input[id*='email']",
                "input[id*='id']"
            ]
            
            for selector in email_selectors:
                try:
                    email_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 이메일 입력 필드 발견 (선택자: {selector})")
                    break
                except:
                    continue
            
            if email_input:
                email_input.clear()
                email_input.send_keys(kakao_email)
                time.sleep(1)
                print("✅ 이메일 입력 완료")
            else:
                print("현재 페이지 소스 (이메일 필드 찾기 실패):")
                print(driver.page_source[:1500])
                raise Exception("이메일 입력 필드를 찾을 수 없습니다")
            
            # 비밀번호 입력 필드 찾기
            print("🔍 비밀번호 입력 필드 찾는 중...")
            password_input = None
            
            # 다양한 방법으로 비밀번호 입력 필드 찾기
            password_selectors = [
                "input[type='password']",
                "input[placeholder*='비밀번호']",
                "input[name='password']",
                "input[id*='password']",
                "input[id*='pw']"
            ]
            
            for selector in password_selectors:
                try:
                    password_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 비밀번호 입력 필드 발견 (선택자: {selector})")
                    break
                except:
                    continue
            
            if password_input:
                password_input.clear()
                password_input.send_keys(kakao_password)
                time.sleep(1)
                print("✅ 비밀번호 입력 완료")
            else:
                print("현재 페이지 소스 (비밀번호 필드 찾기 실패):")
                print(driver.page_source[:1500])
                raise Exception("비밀번호 입력 필드를 찾을 수 없습니다")
            
            # 로그인 버튼 찾기
            print("🔍 로그인 버튼 찾는 중...")
            login_button = None
            
            # 다양한 방법으로 로그인 버튼 찾기
            login_selectors = [
                "button[type='submit']",
                "//button[contains(text(), '로그인')]",
                "button.btn_login",
                "button[class*='login']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Sign in')]",
                "//button[contains(text(), 'Login')]"
            ]
            
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = driver.find_element(By.XPATH, selector)
                    else:
                        login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 로그인 버튼 발견 (선택자: {selector})")
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                time.sleep(5)  # 로그인 처리 대기 시간 증가
                print("✅ 로그인 버튼 클릭 완료")
            else:
                print("현재 페이지 소스 (로그인 버튼 찾기 실패):")
                print(driver.page_source[:1500])
                raise Exception("로그인 버튼을 찾을 수 없습니다")
            
            print("✅ 카카오 로그인 완료!")
            
        except Exception as e:
            print(f"❌ 카카오 자동 로그인 실패: {e}")
            print("수동 로그인을 진행합니다...")
    else:
        print("카카오 계정 정보가 없어 수동 로그인을 진행합니다...")
    
    # 4. 티스토리 글쓰기 페이지로 이동
    print("📝 티스토리 글쓰기 페이지로 이동 중...")
    
    # 페이지 이동 전에 알림창이 있는지 확인
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"페이지 이동 전 알림창 감지: {alert_text}")
        
        # 저장된 글 이어서 작성 여부 묻는 알림창인 경우 "아니오" 선택
        if "저장된 글이 있습니다" in alert_text and "이어서 작성하시겠습니까" in alert_text:
            alert.dismiss()  # 아니오 클릭
            print("✅ 저장된 글 이어서 작성 알림창을 '아니오'로 처리")
        else:
            alert.accept()  # 기타 알림창은 확인(예) 클릭
        time.sleep(1)
    except NoAlertPresentException:
        pass
    except Exception as e:
        print(f"페이지 이동 전 알림창 처리 중 오류: {e}")
    
    # 페이지 이동
    driver.get(f"{blog_url}/manage/newpost/?type=post")
    time.sleep(5)  # 페이지 로딩 대기 시간 증가
    
    # 5. 알림(팝업) 자동 닫기
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"페이지 이동 후 알림창 감지: {alert_text}")
        
        # 저장된 글 이어서 작성 여부 묻는 알림창인 경우 "아니오" 선택
        if "저장된 글이 있습니다" in alert_text and "이어서 작성하시겠습니까" in alert_text:
            alert.dismiss()  # 아니오 클릭
            print("✅ 저장된 글 이어서 작성 알림창을 '아니오'로 처리")
        else:
            alert.accept()  # 기타 알림창은 확인(예) 클릭
        time.sleep(1)
    except NoAlertPresentException:
        pass
    except Exception as e:
        print(f"페이지 이동 후 알림창 처리 중 오류: {e}")
    
    # 6. 로그인 확인 및 대기
    if "login" in driver.current_url or "kakao.com" in driver.current_url:
        print("로그인이 필요합니다. 로그인 후 엔터를 누르세요...")
        input()
        driver.get(f"{blog_url}/manage/newpost/?type=post")
        time.sleep(3)

    # 7. React 앱 로딩 대기
    print("⏳ 글쓰기 페이지 로딩 대기 중...")
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[placeholder*='제목'], .textarea_tit"))
        )
        print("✅ 글쓰기 페이지 로딩 완료")
    except TimeoutException:
        print("⚠️ 글쓰기 페이지 로딩 시간 초과, 계속 진행...")

    # 8. 제목 입력
    print("📝 제목 입력 중...")
    title_box = None
    try:
        # 다양한 방법으로 제목 입력 필드 찾기
        try:
            title_box = driver.find_element(By.CSS_SELECTOR, "textarea.textarea_tit")
        except:
            try:
                title_box = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='제목']")
            except:
                try:
                    title_box = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='제목']")
                except:
                    title_box = driver.find_element(By.CSS_SELECTOR, "input[name='title']")
        
        if title_box:
            title_box.clear()
            title_box.send_keys(title)
            time.sleep(1)
            print("✅ 제목 입력 완료")
        else:
            raise Exception("제목 입력 필드를 찾을 수 없습니다")
    except Exception as e:
        print(f"❌ 제목 입력 오류: {e}")
        # 페이지 소스 출력으로 디버깅
        print("현재 페이지 소스:")
        print(driver.page_source[:2000])

    # 8.5. 에디터 모드를 마크다운으로 변경
    print("🔄 에디터 모드를 마크다운으로 변경 중...")
    
    # 디버깅: 제공해주신 XPath 요소 확인
    try:
        debug_element = driver.find_element(By.XPATH, "/html/body/div[8]")
        print(f"🔍 디버깅: /html/body/div[8] 요소 발견")
        print(f"   - 태그: {debug_element.tag_name}")
        print(f"   - 텍스트: {debug_element.text[:100]}...")
        print(f"   - 클래스: {debug_element.get_attribute('class')}")
        print(f"   - ID: {debug_element.get_attribute('id')}")
    except Exception as e:
        print(f"⚠️ 디버깅: /html/body/div[8] 요소를 찾을 수 없음 - {e}")
    
    try:
        # 1. 드롭다운(기본모드) 버튼 찾기 - 여러 방법 시도
        mode_btn = None
        mode_selectors = [
            "#editor-mode-layer-btn",
            "button[class*='mode']",
            "button[class*='editor']",
            "//button[contains(text(), '기본모드')]",
            "//button[contains(text(), '모드')]",
            "//div[contains(@class, 'mode') and contains(@class, 'btn')]",
            "//button[contains(@class, 'mode')]",
            "//div[contains(@class, 'editor-mode')]",
            "/html/body/div[8]"  # 제공해주신 XPath 추가
        ]
        
        for selector in mode_selectors:
            try:
                if selector.startswith("//"):
                    mode_btn = driver.find_element(By.XPATH, selector)
                else:
                    mode_btn = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ 에디터 모드 버튼 발견 (선택자: {selector})")
                break
            except:
                continue
        
        if mode_btn:
            mode_btn.click()
            time.sleep(2)  # 드롭다운 메뉴 로딩 대기 시간 증가
            print("✅ 에디터 모드 드롭다운 클릭 완료")
        else:
            raise Exception("에디터 모드 버튼을 찾을 수 없습니다")

        # 2. "마크다운" 항목 찾기 - 제공해주신 정확한 XPath 사용
        markdown_mode = None
        try:
            markdown_mode = driver.find_element(By.XPATH, '//*[@id="editor-mode-markdown-text"]')
            print("✅ 마크다운 모드 항목 발견 (선택자: //*[@id='editor-mode-markdown-text'])")
        except:
            # 백업 방법들
            markdown_selectors = [
                "div#editor-mode-markdown",
                "//div[contains(text(), '마크다운')]",
                "//button[contains(text(), '마크다운')]",
                "//span[contains(text(), '마크다운')]",
                "//*[contains(text(), '마크다운')]",
                "button[class*='markdown']",
                "div[class*='markdown']",
                "//li[contains(text(), '마크다운')]",
                "//option[contains(text(), '마크다운')]"
            ]
            
            for selector in markdown_selectors:
                try:
                    if selector.startswith("//"):
                        markdown_mode = driver.find_element(By.XPATH, selector)
                    else:
                        markdown_mode = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 마크다운 모드 항목 발견 (선택자: {selector})")
                    break
                except:
                    continue
        
        if markdown_mode:
            markdown_mode.click()
            time.sleep(1)  # 클릭 후 대기
            print("✅ 마크다운 모드 선택 완료")
            
            # 마크다운 모드 선택 직후 alert 처리
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"🔍 마크다운 모드 전환 알림창 감지: {alert_text}")
                alert.accept()  # 확인 클릭
                print("✅ 마크다운 모드 전환 알림창 '확인' 클릭 완료")
                time.sleep(1)
            except NoAlertPresentException:
                print("ℹ️ 마크다운 모드 전환 알림창 없음")
            except Exception as e:
                print(f"⚠️ 마크다운 모드 전환 알림창 처리 중 오류: {e}")
        else:
            # 마크다운 항목을 찾지 못한 경우, 키보드로 직접 선택 시도
            print("⚠️ 마크다운 항목을 찾을 수 없어 키보드로 선택 시도...")
            from selenium.webdriver.common.keys import Keys
            driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)  # 첫 번째 항목으로 이동
            time.sleep(0.5)
            driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)  # 두 번째 항목(마크다운)으로 이동
            time.sleep(0.5)
            driver.switch_to.active_element.send_keys(Keys.ENTER)
            time.sleep(1)
            print("✅ 키보드로 마크다운 모드 선택 완료")
            
            # 키보드 선택 후에도 alert 처리
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"🔍 키보드 선택 후 알림창 감지: {alert_text}")
                alert.accept()  # 확인 클릭
                print("✅ 키보드 선택 후 알림창 '확인' 클릭 완료")
                time.sleep(1)
            except NoAlertPresentException:
                print("ℹ️ 키보드 선택 후 알림창 없음")
            except Exception as e:
                print(f"⚠️ 키보드 선택 후 알림창 처리 중 오류: {e}")

        # 3. 추가 알림창 처리 (혹시 다른 알림창이 있을 경우)
        print("🔍 추가 알림창 확인 중...")
        time.sleep(1)
        
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"🔍 추가 알림창 감지: {alert_text}")
            alert.accept()  # 확인 클릭
            print("✅ 추가 알림창 '확인' 클릭 완료")
            time.sleep(1)
        except NoAlertPresentException:
            print("ℹ️ 추가 알림창 없음")
        except Exception as e:
            print(f"⚠️ 추가 알림창 처리 중 오류: {e}")
        
        print("✅ 에디터 모드를 마크다운으로 변경 완료")
        
    except Exception as e:
        print(f"⚠️ 에디터 모드(마크다운) 변경 오류: {e}")
        print("⚠️ 마크다운 모드 변경에 실패했지만 계속 진행합니다...")

    # --- JSON 본문 포함 보장 ---
    # 마크다운 파일 읽기 후 json_file 인자가 있으면 json_data로 로드
    # (이 코드는 함수 맨 앞부분에 위치해야 함)
    # ... 기존 코드 ...
    # 1. 마크다운 파일 읽기
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    title = ""
    body_lines = []
    for line in lines:
        if line.startswith('# ') and not title:
            title = line[2:].strip()
        else:
            body_lines.append(line)
    if not title:
        title = os.path.basename(markdown_file).replace('.md', '')
    body = '\n'.join(body_lines).strip()

    # json_file 인자가 있으면 json_data로 로드
    if json_file and (not json_data):
        import json
        try:
            with open(json_file, 'r', encoding='utf-8') as jf:
                json_data = json.load(jf)
            print(f"✅ JSON 파일 로드 완료: {json_file}")
        except Exception as e:
            print(f"⚠️ JSON 파일 로드 실패: {e}")
            json_data = None

    # JSON 데이터가 있으면 본문에 반드시 포함
    html_body = markdown_to_html(body, json_data)

    # 9. 본문 입력
    print("📝 본문 입력 중...")
    try:
        from selenium.webdriver.common.keys import Keys  # Keys import 위치 보강
        
        # 본문 입력 전에 알림창 처리
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"본문 입력 전 알림창 감지: {alert_text}")
            
            # 작성 모드 변경 알림창인 경우 "확인" 선택
            if "작성 모드를 변경하시겠습니까" in alert_text:
                alert.accept()  # 확인 클릭
                print("✅ 작성 모드 변경 알림창을 '확인'으로 처리")
                time.sleep(1)
            else:
                alert.accept()  # 기타 알림창은 확인(예) 클릭
        except NoAlertPresentException:
            pass
        except Exception as e:
            print(f"본문 입력 전 알림창 처리 중 오류: {e}")
        
        # 마크다운 모드인지 확인하고 적절한 입력 방법 선택
        try:
            # 제목 입력란에서 현재 모드 확인
            title_input = driver.find_element(By.CSS_SELECTOR, "#post-title-inp")
            placeholder = title_input.get_attribute("placeholder")
            print(f"제목 입력란 placeholder: {placeholder}")
            
            # 마크다운 모드인 경우 (제목/본문 분리 입력)
            if "제목을 입력하세요" in placeholder:
                print("📝 마크다운 모드로 제목/본문 입력...")
                # 제목 추출
                md_lines = body.split('\n')
                md_title = ""
                md_body_lines = []
                for line in md_lines:
                    if line.startswith('# ') and not md_title:
                        md_title = line[2:].strip()
                    else:
                        md_body_lines.append(line)
                if not md_title:
                    md_title = os.path.basename(markdown_file).replace('.md', '')
                md_body = '\n'.join(md_body_lines).strip()
                # 제목 입력
                title_input.clear()
                title_input.send_keys(Keys.CONTROL, 'a')
                title_input.send_keys(Keys.DELETE)
                title_input.send_keys(md_title)
                print(f"✅ 마크다운 모드 제목 입력: {md_title}")
                # 본문 입력 (CodeMirror 마크다운 에디터)
                try:
                    print(f"[디버그] 입력할 md_body 내용 (앞 200자):\n{md_body[:200]}")
                    # 정확한 CodeMirror div 선택 (마크다운 모드)
                    driver.execute_script('''
                        var cm = document.querySelector('.CodeMirror.cm-s-tistory-markdown');
                        if (cm && cm.CodeMirror) {
                            // 1. CodeMirror에 값 설정
                            cm.CodeMirror.setValue(arguments[0]);
                            cm.CodeMirror.save();
                            
                            // 2. 모든 관련 이벤트 트리거
                            cm.CodeMirror.getInputField().dispatchEvent(new Event('change', {bubbles: true}));
                            cm.CodeMirror.getInputField().dispatchEvent(new Event('input', {bubbles: true}));
                            cm.CodeMirror.getInputField().dispatchEvent(new Event('blur', {bubbles: true}));
                            cm.CodeMirror.getInputField().dispatchEvent(new Event('focus', {bubbles: true}));
                            
                            // 3. 티스토리 에디터의 내부 textarea 이벤트도 트리거
                            var textarea = cm.querySelector('textarea');
                            if (textarea) {
                                textarea.dispatchEvent(new Event('change', {bubbles: true}));
                                textarea.dispatchEvent(new Event('input', {bubbles: true}));
                            }
                            
                            // 4. React 컴포넌트의 상태 업데이트를 위한 커스텀 이벤트
                            var customEvent = new CustomEvent('tistory-editor-update', {
                                detail: { content: arguments[0] },
                                bubbles: true
                            });
                            cm.dispatchEvent(customEvent);
                            
                            // 5. 티스토리 에디터의 내부 상태 강제 업데이트
                            var editorContainer = document.querySelector('#markdown-editor-container');
                            if (editorContainer) {
                                editorContainer.dispatchEvent(new Event('change', {bubbles: true}));
                            }
                        }
                    ''', md_body)
                    
                    # 추가: 키보드 입력 시뮬레이션으로 UI 업데이트 강제
                    try:
                        from selenium.webdriver.common.keys import Keys
                        cm_element = driver.find_element(By.CSS_SELECTOR, ".CodeMirror.cm-s-tistory-markdown")
                        cm_element.click()
                        actions = ActionChains(driver)
                        actions.move_to_element(cm_element)
                        actions.click()
                        actions.send_keys(Keys.CONTROL + "a")  # 전체 선택
                        actions.send_keys(Keys.DELETE)  # 기존 내용 삭제
                        actions.send_keys(md_body)  # 새 내용 입력
                        actions.perform()
                        print("✅ 키보드 입력 시뮬레이션으로 본문 입력 완료")
                    except Exception as e:
                        print(f"⚠️ 키보드 입력 시뮬레이션 실패: {e}")
                        
                        # 백업 방법: 기본모드에서 먼저 입력한 후 마크다운으로 전환
                        print("🔄 백업 방법: 기본모드에서 입력 후 마크다운으로 전환 시도...")
                        try:
                            # 기본모드로 전환
                            mode_btn = driver.find_element(By.CSS_SELECTOR, "#editor-mode-layer-btn")
                            mode_btn.click()
                            time.sleep(1)
                            
                            # 기본모드 선택
                            basic_mode = driver.find_element(By.XPATH, "//*[@id='editor-mode-kakao-tistory']")
                            basic_mode.click()
                            time.sleep(2)
                            
                            # 기본모드에서 iframe 내부에 HTML 입력
                            iframe = driver.find_element(By.CSS_SELECTOR, "iframe#editor-tistory_ifr")
                            driver.switch_to.frame(iframe)
                            body_box = driver.find_element(By.CSS_SELECTOR, "body")
                            body_box.clear()
                            body_box.send_keys(Keys.CONTROL, 'a')
                            body_box.send_keys(Keys.DELETE)
                            body_box.send_keys(html_body)
                            driver.switch_to.default_content()
                            time.sleep(1)
                            print("✅ 기본모드에서 본문 입력 완료")
                            
                            # 다시 마크다운 모드로 전환
                            mode_btn = driver.find_element(By.CSS_SELECTOR, "#editor-mode-layer-btn")
                            mode_btn.click()
                            time.sleep(1)
                            markdown_mode = driver.find_element(By.XPATH, "//*[@id='editor-mode-markdown-text']")
                            markdown_mode.click()
                            time.sleep(2)
                            print("✅ 마크다운 모드로 재전환 완료")
                            
                        except Exception as e2:
                            print(f"❌ 백업 방법도 실패: {e2}")
                except Exception as e:
                    print(f"❌ 마크다운 본문 입력 오류(JS): {e}")
                time.sleep(1)
            else:
                # 기본모드인 경우 (iframe 내부에 HTML 입력)
                print("📝 기본모드로 iframe 내부에 HTML 입력...")
                print("🔍 TinyMCE iframe(editor-tistory_ifr) 진입 시도...")
                iframe = driver.find_element(By.CSS_SELECTOR, "iframe#editor-tistory_ifr")
                driver.switch_to.frame(iframe)
                body_box = driver.find_element(By.CSS_SELECTOR, "body")
                body_box.clear()
                body_box.send_keys(Keys.CONTROL, 'a')
                body_box.send_keys(Keys.DELETE)
                body_box.send_keys(html_body)
                driver.switch_to.default_content()
                time.sleep(1)
                print("✅ 기본모드로 iframe 내부에 HTML 입력 완료")
        except Exception as e:
            print(f"❌ 모드 확인 중 오류: {e}")
            # 오류 발생 시 기본 방법으로 시도
            try:
                print("🔍 TinyMCE iframe(editor-tistory_ifr) 진입 시도...")
                iframe = driver.find_element(By.CSS_SELECTOR, "iframe#editor-tistory_ifr")
                driver.switch_to.frame(iframe)
                body_box = driver.find_element(By.CSS_SELECTOR, "body")
                body_box.clear()
                body_box.send_keys(Keys.CONTROL, 'a')
                body_box.send_keys(Keys.DELETE)
                body_box.send_keys(html_body)
                driver.switch_to.default_content()
                time.sleep(1)
                print("✅ 기본 방법으로 본문 입력 완료")
            except Exception as e2:
                print(f"❌ 기본 방법으로도 본문 입력 실패: {e2}")
                try:
                    driver.switch_to.default_content()
                except:
                    pass
    except Exception as e:
        print(f"❌ 본문 입력 오류: {e}")
        try:
            driver.switch_to.default_content()
        except:
            pass

    # 10. 카테고리 선택
    print("📂 카테고리 선택 중...")
    
    # 디버깅: 제공해주신 새로운 XPath 요소 확인
    try:
        debug_category_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[5]/div/div/div[1]/div/div/div/div/div/div[5]")
        print(f"🔍 디버깅: 카테고리 관련 요소 발견")
        print(f"   - 태그: {debug_category_element.tag_name}")
        print(f"   - 텍스트: {debug_category_element.text[:100]}...")
        print(f"   - 클래스: {debug_category_element.get_attribute('class')}")
        print(f"   - ID: {debug_category_element.get_attribute('id')}")
    except Exception as e:
        print(f"⚠️ 디버깅: 카테고리 관련 요소를 찾을 수 없음 - {e}")
    
    try:
        # 다양한 방법으로 카테고리 버튼 찾기
        category_btn = None
        try:
            category_btn = driver.find_element(By.CSS_SELECTOR, "button.btn_category")
        except:
            try:
                category_btn = driver.find_element(By.XPATH, "//button[contains(text(), '카테고리')]")
            except:
                try:
                    category_btn = driver.find_element(By.CSS_SELECTOR, "button[class*='category']")
                except:
                    try:
                        category_btn = driver.find_element(By.CSS_SELECTOR, "select[name='category']")
                    except:
                        try:
                            category_btn = driver.find_element(By.XPATH, "//select[contains(@name, 'category')]")
                        except:
                            # 제공해주신 새로운 XPath 시도
                            category_btn = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[5]/div/div/div[1]/div/div/div/div/div/div[5]")
        
        if category_btn:
            category_btn.click()
            time.sleep(1)
            
            # 카테고리 목록에서 선택
            try:
                category_item = driver.find_element(By.XPATH, f"//span[text()='{category_name}']")
                category_item.click()
                time.sleep(0.5)
                print(f"✅ 카테고리 '{category_name}' 선택 완료")
            except:
                # 드롭다운에서 선택
                try:
                    category_select = driver.find_element(By.CSS_SELECTOR, "select[name='category']")
                except:
                    category_select = driver.find_element(By.XPATH, "//select[contains(@name, 'category')]")
                from selenium.webdriver.support.ui import Select
                select = Select(category_select)
                select.select_by_visible_text(category_name)
                print(f"✅ 카테고리 '{category_name}' 선택 완료")
        else:
            print("⚠️ 카테고리 버튼을 찾을 수 없습니다")
    except Exception as e:
        print(f"⚠️ 카테고리 선택 오류: {e}")

    # 11. 태그 입력
    print("🏷️ 태그 입력 중...")
    try:
        from selenium.webdriver.common.keys import Keys  # Keys import 위치 보강
        # 다양한 방법으로 태그 입력 필드 찾기
        tag_input = None
        try:
            tag_input = driver.find_element(By.CSS_SELECTOR, "input.input_tag")
        except:
            try:
                tag_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='태그']")
            except:
                try:
                    tag_input = driver.find_element(By.CSS_SELECTOR, "input[name='tag']")
                except:
                    try:
                        tag_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, '태그')]")
                    except:
                        tag_input = driver.find_element(By.XPATH, "//input[contains(@name, 'tag')]")
        
        if tag_input:
            tag_input.clear()
            tag_input.send_keys(tags)
            tag_input.send_keys(Keys.ENTER)
            time.sleep(0.5)
            print("✅ 태그 입력 완료")
        else:
            print("⚠️ 태그 입력 필드를 찾을 수 없습니다")
    except Exception as e:
        print(f"⚠️ 태그 입력 오류: {e}")

    # 12. 발행 버튼 클릭
    print("🚀 발행 버튼 클릭 중...")
    try:
        publish_layer_btn = driver.find_element(By.CSS_SELECTOR, "#publish-layer-btn")
        publish_layer_btn.click()
        print("✅ 1차 완료 버튼 클릭!")

        # 발행 세부 레이어 대기 후 공개 설정 변경
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish-btn"))
        )
        
        # 공개 설정을 "공개"로 변경
        print("🔓 공개 설정을 '공개'로 변경 중...")
        try:
            public_radio = driver.find_element(By.CSS_SELECTOR, "input#open20")
            public_radio.click()
            time.sleep(1)
            print("✅ 공개 설정 변경 완료")
        except Exception as e:
            print(f"⚠️ 공개 설정 변경 오류: {e}")
        
        # 공개 발행 버튼 클릭
        publish_btn = driver.find_element(By.CSS_SELECTOR, "#publish-btn")
        publish_btn.click()
        print("✅ 공개 발행 버튼 클릭 완료!")
    except Exception as e:
        print(f"❌ 발행 버튼 클릭 오류: {e}")

    # 13. 완료 대기 후 종료
    print("⏳ 발행 처리 대기 중...")
    time.sleep(5)
    driver.quit()
    print("�� 티스토리 자동 업로드 완료!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="티스토리 셀레니움 자동 포스팅")
    parser.add_argument('--file', required=True, help='마크다운 파일 경로')
    parser.add_argument('--blog', required=True, help='블로그 주소 (예: https://aigent-hong.tistory.com)')
    parser.add_argument('--category', default='IT', help='카테고리명')
    parser.add_argument('--tags', default='BBC뉴스,글로벌트렌드,기술동향', help='태그(쉼표구분)')
    parser.add_argument('--headless', action='store_true', help='브라우저 창 숨김')
    parser.add_argument('--kakao-email', help='카카오 이메일 (자동 로그인용)')
    parser.add_argument('--kakao-password', help='카카오 비밀번호 (자동 로그인용)')
    parser.add_argument('--json-file', help='JSON 파일 경로 (본문에 포함할 데이터)') # 추가된 인자
    args = parser.parse_args()
    tistory_post_with_selenium(
        markdown_file=args.file,
        blog_url=args.blog,
        category_name=args.category,
        tags=args.tags,
        headless=args.headless,
        kakao_email=args.kakao_email,
        kakao_password=args.kakao_password,
        json_file=args.json_file # 추가된 인자 전달
    ) 