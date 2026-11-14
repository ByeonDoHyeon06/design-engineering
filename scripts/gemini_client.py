#!/usr/bin/env python3
"""Optional Gemini REST JSON client. stdlib only. No key logging / no arbitrary URLs."""
import json, os, re, time, urllib.error, urllib.request

HOST='https://generativelanguage.googleapis.com/v1beta/models/'
class GeminiError(RuntimeError): pass

def generate_json(prompt, *, model='gemini-3.6-flash', timeout=30, api_key=None, opener=None):
    key=api_key or os.environ.get('GEMINI_API_KEY')
    if not key: raise GeminiError('GEMINI_API_KEY is not configured; local mode is available.')
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{2,100}',model):
        raise GeminiError('Invalid model identifier.')
    if not isinstance(prompt,str) or not prompt or len(prompt)>100000:
        raise GeminiError('Invalid or excessive prompt length.')
    data=json.dumps({'contents':[{'role':'user','parts':[{'text':prompt}]}],
        'generationConfig':{'responseMimeType':'application/json','temperature':0.15}},ensure_ascii=False).encode('utf-8')
    request=urllib.request.Request(HOST+model+':generateContent',data=data,
        headers={'Content-Type':'application/json','x-goog-api-key':key},method='POST')
    send=opener or urllib.request.urlopen
    last=None
    for attempt in range(3):
        try:
            with send(request, timeout=timeout) as response:
                obj=json.loads(response.read(2_000_000).decode('utf-8'))
            text=''.join(part.get('text','') for part in obj.get('candidates',[{}])[0].get('content',{}).get('parts',[]))
            if not text.strip(): raise GeminiError('No usable text returned by Gemini.')
            return json.loads(text)
        except urllib.error.HTTPError as exc:
            # HTTP errors are deliberately sanitized: never print response or credentials.
            last=GeminiError(f'Gemini HTTP {exc.code}; check API key/model/quota.')
            if exc.code not in (429,500,502,503,504) or attempt==2: raise last from None
            time.sleep(.3*(attempt+1))
        except (urllib.error.URLError, TimeoutError) as exc:
            last=GeminiError('Gemini connection failed or timed out.')
            if attempt==2: raise last from None
            time.sleep(.3*(attempt+1))
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise GeminiError('Gemini returned invalid JSON or response shape.') from None
    raise last or GeminiError('Gemini request unsuccessful.')
