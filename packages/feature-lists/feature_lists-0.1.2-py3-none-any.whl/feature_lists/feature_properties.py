from core.models import Video
from userauths.models import Profile
from channel.models import Channel

class FeatureManager:

    @staticmethod
    def s_video(request, id):
        video =Video.objects.get(id=id)
        user = Profile.objects.get(user=request.user)
    
        if video in user.saved_videos.all():
            user.saved_videos.remove(video)
        else:
            user.saved_videos.add(video)    


    @staticmethod
    def l_video(request, id):
        video = Video.objects.get(id=id)
        user = Profile.objects.get(user=request.user)
    
        if video in user.liked_videos.all():
            user.liked_videos.remove(video)
        else:
            user.liked_videos.add(video)      
            
                      
    @staticmethod
    def channel_d(request):
        channel = Channel.objects.get(user=request.user)
        videos = Video.objects.filter(user=request.user)
        videos.delete()
        channel.delete()  
              
    
    @staticmethod
    def video_d(request, video_id,channel_id):
        user = request.user
        video = Video.objects.get(id=video_id)
        channel = Channel.objects.get(id=channel_id)
        video.delete()
     
        