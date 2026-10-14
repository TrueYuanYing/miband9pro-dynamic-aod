/* Firmware-specific RAM extension. First hardware execution is experimental. */
#include <stdint.h>
#include <stddef.h>

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define SCREEN 0x200b6680u
#define ORIGINAL 0x0c368c6du
#define SLOT (SCREEN + 0x20cu)
#define MAGIC 0x36314f41u
#define FN(a,t) ((t)(uintptr_t)(a))
typedef void (*leaf)(void);
typedef void (*screen_fn)(int,int);
typedef int (*start_fn)(void *,void (*)(void *),uint64_t,uint64_t);

struct context {
    uint32_t magic,version,enabled,ready;
    _Alignas(8) uint8_t timer[88];
    void *loop;
    uint32_t pending;
    uint64_t deadline;
    uint32_t playing,session;
    void (*hook)(int,int);
    void (*pulse)(void *);
    void (*defer)(void *);
    void *lv_timer;
    uint32_t image,size,pulses,error;
};
struct request {
    int32_t result;
    uint32_t context,source,size,hook_offset,pulse_offset,defer_offset;
};
_Static_assert(offsetof(struct context,timer)==16,"timer ABI");
_Static_assert(offsetof(struct context,enabled)==8,"Lua control ABI");
_Static_assert(sizeof(struct context)==160,"resident receipt ABI");
_Static_assert(offsetof(struct context,image)==144,"resident image ABI");

static void barriers(void) { __asm__ volatile("dsb sy\nisb sy" ::: "memory"); }
static uint32_t lock(void) { uint32_t p; __asm__ volatile("mrs %0,primask\ncpsid i":"=r"(p)::"memory");return p; }
static void unlock(uint32_t p) { __asm__ volatile("msr primask,%0"::"r"(p):"memory"); }
static int privileged(void) {
    uint32_t c,i;__asm__ volatile("mrs %0,control\nmrs %1,ipsr":"=r"(c),"=r"(i));
    return !(c&1) && !i && WORD(0xe000ed94)==5 && WORD(0xe000edc0)==0x00447722;
}
static int in_heap(uint32_t p,uint32_t n) {
    return WORD(0x200b17f4)==0x3cf7e080u && p>WORD(0x3cf7e094u)
        && p<0x3dff0000u && n<=0x3dff0000u-p && p+n<=WORD(0x3cf7e098u);
}
static int executable_range(uint32_t data,uint32_t size) {
    if(!in_heap(data,size)) return 0;
    uint32_t base=data-0x20000000u,last=base+size-1u;
    uint32_t p=lock(),old=WORD(0xe000ed98),ok=1;
    for(uint32_t id=0;id<8;id++) {
        WORD(0xe000ed98)=id;
        uint32_t b=WORD(0xe000ed9c),l=WORD(0xe000eda0);
        if((l&1u) && base<=(l|31u) && last>=(b&~31u)) ok=0;
    }
    WORD(0xe000ed98)=old;barriers();unlock(p);return ok;
}
static int publish(void) {
    if(!(WORD(0x07ffa000)&1) || !(WORD(0x07ffc000)&1))return -1;
    /* Both enabled branches clean/invalidate; D (selector 1) precedes I (0). */
    FN(0x0c08208bu,leaf)();barriers();FN(0x0c0820a3u,leaf)();barriers();return 0;
}
static int state(void) { return FN(0x0c44a9a5u,int (*)(void))(); }
static uint64_t now(struct context *c) {
    FN(0x0c114d91u,void (*)(void *))(c->loop);
    return *(volatile uint64_t *)((uintptr_t)c->loop+0x140u);
}
static void stop(struct context *c,int reset) {
    c->playing=0;c->pending=0;if(reset)c->session=0;
    if(c->ready)FN(0x0c111f63u,int (*)(void *))(c->timer);
}
static int schedule(struct context *c,uint64_t delay) {
    int rc=FN(0x0c112069u,start_fn)(c->timer,c->pulse,delay,0);
    if(rc){c->error=4;stop(c,1);}return rc;
}
void native_pulse(void *handle) {
    struct context *c=*(struct context **)handle;
    if(!c || c->magic!=MAGIC || !c->ready)return;
    if(!c->enabled || state()!=1){stop(c,1);return;}
    uint64_t t=now(c);
    if(c->pending) {
        c->pending=0;if(c->session)return;
        c->session=1;c->playing=1;c->deadline=t+12000u;c->pulses=0;
    }
    if(!c->playing)return;
    FN(0x0c455a29u,leaf)();c->pulses++;
    if(!c->enabled || state()!=1){stop(c,1);return;}
    /* Lua marks 2 only after setting the terminal image. The original queue's
     * display event has now been issued; this still is not a panel flush ACK.
     * A hard ceiling prevents endless activity if Lua fails to signal. */
    if(c->enabled==2u){stop(c,0);return;}
    if(t>=c->deadline){c->error=5u;stop(c,0);return;}
    uint64_t d=c->deadline-t;schedule(c,d<100u?d:100u);
}
static void arm(struct context *c) {
    if(!c->enabled || !c->ready || c->session)return;
    c->pending=1;schedule(c,100u);
}
void screen_hook(int enable,int flush,struct context *c) {
    FN(ORIGINAL,screen_fn)(enable,flush);
    if(!c || c->magic!=MAGIC || !c->ready)return;
    if(enable || !c->enabled)stop(c,1);else arm(c);
}
void native_deferred(void *timer) {
    /* Exact lv_timer_create stores its user_data at +0xc. */
    struct context *c=*(struct context **)((uintptr_t)timer+12u);
    /* Pause, rather than freeing a linked callback while its handler runs. */
    *(volatile uint8_t *)((uintptr_t)timer+20u)|=1u;
    if(!c || c->magic!=MAGIC || c->ready)return;
    c->loop=(void *)(uintptr_t)WORD(SCREEN);
    if(!c->loop){c->error=1;return;}
    if(FN(0x0c111f31u,int (*)(void *,void *))(c->loop,c->timer)) {c->error=2;return;}
    *(struct context **)c->timer=c;c->ready=1;
    if(state()==1)arm(c);
}
int bootstrap(struct request *r) {
    if(!r || !in_heap((uint32_t)(uintptr_t)r,sizeof(*r)))return -1;
    r->result=-101;
    if(!privileged() || !executable_range(r->source,r->size))return -101;
    if(r->size<32u || r->size>16384u || r->hook_offset>=r->size
       ||r->pulse_offset>=r->size||r->defer_offset>=r->size)return r->result=-102;
    if(WORD(SLOT)!=ORIGINAL)return r->result=-103;
    /* Original mm_mallinfo returns six words through a hidden result pointer.
     * mxordblk is word 3. Headroom reduces, but cannot eliminate, allocation
     * races with other tasks; physical OOM behaviour remains untested. */
    uint32_t info[6]={0};
    FN(0x0c0f1c71u,void (*)(uint32_t *,void *))(info,(void *)0x3cf7e080u);
    uint32_t n=(r->size+31u)&~31u;
    uint32_t total=n+((sizeof(struct context)+31u)&~31u);
    if(info[3]<total+65536u)return r->result=-104;
    void *allocation=FN(0x0c0f21edu,void *(*)(uint32_t,uint32_t))(32,total);
    if(!allocation)return r->result=-105;
    struct context *c=allocation;
    if(!in_heap((uint32_t)(uintptr_t)c,total))return r->result=-106;
    uint32_t image=(uint32_t)(uintptr_t)c+((sizeof(*c)+31u)&~31u);
    if(!executable_range(image,n)) {
        FN(0x0c0f1b01u,void (*)(void *))(allocation);return r->result=-107;
    }
    for(uint32_t i=0;i<total;i++)((volatile uint8_t *)allocation)[i]=0;
    for(uint32_t i=0;i<r->size;i++)((volatile uint8_t *)(uintptr_t)image)[i]=((volatile uint8_t *)(uintptr_t)r->source)[i];
    c->magic=MAGIC;c->version=16;c->enabled=1;c->image=image;c->size=r->size;
    uint32_t exec=image-0x20000000u;
    c->hook=(void (*)(int,int))(uintptr_t)(exec+(r->hook_offset&~1u)+1u);
    c->pulse=(void (*)(void *))(uintptr_t)(exec+(r->pulse_offset&~1u)+1u);
    c->defer=(void (*)(void *))(uintptr_t)(exec+(r->defer_offset&~1u)+1u);
    WORD(image+4u)=(uint32_t)(uintptr_t)c;
    if(publish()) {
        FN(0x0c0f1b01u,void (*)(void *))(allocation);return r->result=-108;
    }
    uint32_t p=lock();
    if(WORD(SLOT)!=ORIGINAL){unlock(p);FN(0x0c0f1b01u,void (*)(void *))(allocation);return r->result=-109;}
    WORD(SLOT)=(uint32_t)(uintptr_t)c->hook;barriers();unlock(p);
    r->context=(uint32_t)(uintptr_t)c;
    /* As in the public native-app loader: only create the timer here. Actual
     * libuv and redraw work is deferred into the firmware's LVGL/UI handler. */
    c->lv_timer=FN(0x0c25cb8du,void *(*)(void (*)(void *),uint32_t,void *))(c->defer,0,c);
    if(!c->lv_timer){c->enabled=0;c->error=3;WORD(SLOT)=ORIGINAL;return r->result=-110;}
    return r->result=0;
}
