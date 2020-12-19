typedef struct PWAPoint  
{  
    RtPoint point;  
    int  flag;//0表示被剪裁多边形，1表示交点  
    int  index;//属于被剪裁哪个线段的交点  
    int index0;//属于剪裁哪个线段的交点  
    int  flag0;//0表示入，1表示出,-1表示清除  
}PWAPoint;  
  
typedef struct PWAArray  
{  
    double dist;//交点于启点的距离  
    int index;//交点存储位置  
}PWAArray;  
  
//多边形点必须是顺时针方向  
int rtPrunePWA(RtPoint* src, int num, RtPoint* dest, int total)  
{  
    int i = 0, j = 0, k = 0,n = 0,m = 0, w = 0,u = 0;  
    RtPoint sp, ep;//剪裁多边形  
    RtPoint startP, endP;//被剪裁多边形  
  
    CRtPoint<double> point;  
    CRtPoint<int> st, et;                   
    CRtLine<int> v1,v2;  
  
    PWAPoint* injectP = (PWAPoint*)malloc(sizeof(PWAPoint) * num * total);  
    PWAPoint* temp = (PWAPoint*)malloc(sizeof(PWAPoint) * num * (total));//剪裁加交点插入  
    PWAPoint* temp0 = (PWAPoint*)malloc(sizeof(PWAPoint) * num * (total));//被剪裁加交点插入  
    PWAArray* inP = (PWAArray*)malloc(sizeof(PWAArray) * num * (total));  
    RtPoint* dst = (RtPoint*)malloc(sizeof(RtPoint) * num * total);//输出数组  
  
    //求交点  
    startP = *(dest + total - 1);  
    for (j = 0; j < total; j++)//被剪裁多边形  
    {  
        endP = *(dest + j);  
        st.SetData(startP.x, startP.y);  
        et.SetData(endP.x, endP.y);  
        v2.SetData(st, et);  
  
        sp = *(src + num - 1);  
        for (i = 0; i < num; i++)//剪裁多边形  
        {  
            ep = *(src + i);  
            st.SetData(sp.x, sp.y);  
            et.SetData(ep.x, ep.y);  
            v1.SetData(st, et);   
              
            if(v2.Intersect(v1,point))//求交点   
            {  
                injectP[k].point.x = point[0];  
                injectP[k].point.y = point[1];  
                injectP[k].flag = 1;  
                injectP[k].index = j;  
                injectP[k].index0 = i;  
            }  
            sp = ep;  
        }  
        startP = endP;  
    }  
  
    //剪裁多边形插入交点  
    w = 0;  
    for (i = 0; i < num; i++)  
    {  
        temp[w].point = *(src + i);  
        temp[w].flag = 0;  
        w++;  
  
        n = 0;  
        for (j = 0; j < k;j++)  
        {  
            if (injectP[j].index0 == j)//属于剪裁当前线段的交点  
            {  
                inP[n].dist = sqrt(pow(injectP[j].point.x - temp[w].point.x , 2) + pow(injectP[j].point.y - temp[w].point.y , 2));  
                inP[n].index = j;  
                n++;  
            }  
        }  
  
        for (j = 0; j<n; j++)  
        {  
            for (m = j+1;m<n;m++)  
            {  
                PWAArray tempp;  
                if (inP[j].dist > inP[m].dist)  
                {  
                    tempp = inP[j];  
                    inP[j] = inP[m];  
                    inP[m] = tempp;  
                }  
            }  
        }  
  
        for (j = 0; j < n;j++)  
        {  
            temp[w] = injectP[inP[j].index];  
            w++;  
        }  
  
    }  
  
    //被剪裁多边形插入交点  
    u = 0;  
    for (i = 0; i < total; i++)  
    {  
        temp0[u].point = *((dest) + i);  
        temp0[u].flag = 0;  
        u++;  
          
        n = 0;  
        for (j = 0; j < k;j++)  
        {  
            if (injectP[j].index0 == j)//属于剪裁当前线段的交点  
            {  
                inP[n].dist = sqrt(pow(injectP[j].point.x - temp0[u].point.x , 2) + pow(injectP[j].point.y - temp0[u].point.y , 2));  
                inP[n].index = j;  
                n++;  
            }  
        }  
          
        for (j = 0; j<n; j++)  
        {  
            for (m = j+1;m<n;m++)  
            {  
                PWAArray tempp;  
                if (inP[j].dist > inP[m].dist)  
                {  
                    tempp = inP[j];  
                    inP[j] = inP[m];  
                    inP[m] = tempp;  
                }  
            }  
        }  
          
        for (j = 0; j < n;j++)  
        {  
            temp0[u] = injectP[inP[j].index];  
            u++;  
        }  
          
    }  
  
    //标记出入点  
    for (i = 0; i < w; i++)  
    {  
        if (temp[i].flag == 1)  
        {  
            if (i == w - 1)  
            {  
                if(temp[0].flag == 0)  
                {  
                    temp[i].flag0 = 0;  
                }  
                if (temp[0].flag == 1)  
                {  
                    temp[i].flag0 = 1;  
                }  
            }  
            else  
            {  
                if (temp[i + 1].flag == 0)  
                {  
                    temp[i].flag0 = 0;  
                }  
                else  
                {  
                    temp[i].flag0 = 1;  
                }  
            }             
        }  
    }  
    for (i = 0; i < u; i++)  
    {  
        if (temp0[i].flag == 1)  
        {  
            if (i == u - 1)  
            {  
                if(temp0[0].flag == 0)  
                {  
                    temp0[i].flag0 = 0;  
                }  
                if (temp0[0].flag == 1)  
                {  
                    temp0[i].flag0 = 1;  
                }  
            }  
            else  
            {  
                if (temp0[i + 1].flag == 0)  
                {  
                    temp0[i].flag0 = 0;  
                }  
                else  
                {  
                    temp0[i].flag0 = 1;  
                }  
            }             
        }  
    }  
  
    k = 0;  
    //统计剪裁区域  
loop3:  
    for (i = 0; i < u; i++)//被剪裁区域  
    {  
        if (0 == temp0[i].flag0)//是入点  
        {  
            dst[k] = temp0[i].point;  
            k++;  
            temp0[i].flag0 = -1;  
            goto loop0;  
        }  
    }  
    return 1;  
  
loop0:  
    for (j = i; j < u; j++)  
    {  
        if (temp0[i].flag0 != 1)//不是出点  
        {  
            dst[k] = temp0[i].point;  
            temp0[i].flag0 = -1;  
            k++;  
        }  
        else  
        {  
            goto loop1;  
        }  
    }  
  
loop1:  
    for (m = 0; m < w; m++)  
    {  
        if (dst[k].x == temp[m].point.x && dst[k].y == temp[m].point.y)  
        {  
            goto loop2;  
        }  
    }  
  
loop2:  
    for (n = m+1;n < w; n++)  
    {  
        if (temp[i].flag0 != 0)//不是入点  
        {  
            dst[k] = temp[i].point;  
            temp[i].flag0 = -1;  
            k++;  
        }  
        else  
        {  
            goto loop3;  
        }  
    }  
  
    free(injectP);  
    free(temp);  
    free(temp0);  
    free(inP);  
    return 0;  
}  