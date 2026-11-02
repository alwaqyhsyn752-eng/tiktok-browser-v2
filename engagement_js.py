JS_LIKE = r"""
(function(){
  var sels = [
    '[data-e2e="like-icon"]',
    '[data-e2e="browse-like-icon"]',
    'button[aria-label*="Like"]',
    'button[aria-label*="like"]',
    '[aria-label*="أعجبني"]'
  ];
  for (var i=0; i<sels.length; i++){
    var el = document.querySelector(sels[i]);
    if (el){
      var t = el.closest('button') || el;
      t.click();
      return JSON.stringify({ok:true, sel:sels[i]});
    }
  }
  return JSON.stringify({ok:false, reason:'no like button'});
})()
"""

JS_COMMENT_TEMPLATE = r"""
(function(){
  var text = %%TEXT%%;
  var input = document.querySelector('[data-e2e="comment-input"], div[contenteditable="true"]');
  if (!input) return JSON.stringify({ok:false, reason:'no comment input'});
  input.focus();
  var tag = input.tagName.toLowerCase();
  if (tag === 'textarea' || tag === 'input'){
    input.value = text;
  } else {
    input.innerText = text;
  }
  input.dispatchEvent(new Event('input', {bubbles:true}));
  var posts = ['[data-e2e="comment-post"]', 'button[type="submit"]', 'button[aria-label*="Post"]', 'button[aria-label*="نشر"]'];
  for (var i=0; i<posts.length; i++){
    var b = document.querySelector(posts[i]);
    if (b && !b.disabled){
      b.click();
      return JSON.stringify({ok:true, sel:posts[i]});
    }
  }
  return JSON.stringify({ok:false, reason:'no post button'});
})()
"""

JS_PAGE_DIAGNOSTICS = r"""
(function(){
  return JSON.stringify({
    url: location.href,
    title: document.title,
    hasLike: !!document.querySelector('[data-e2e="like-icon"],[data-e2e="browse-like-icon"],button[aria-label*="Like"]'),
    hasComment: !!document.querySelector('[data-e2e="comment-input"],div[contenteditable="true"]'),
    videoCount: document.querySelectorAll('video').length
  });
})()
"""
